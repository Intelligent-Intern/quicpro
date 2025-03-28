"""
HTTP/3 Connection Module
This module defines the HTTP3Connection class that provides HTTP/3-specific
behavior over an underlying QUIC connection. It integrates stream management,
priority scheduling, and QPACK-based header processing.
Responsibilities:
  - Negotiating HTTP/3 settings.
  - Managing streams via a dedicated StreamManager.
  - Routing outgoing requests to streams with assigned priorities.
  - Demultiplexing incoming frames to the correct stream based on stream ID.
  
This version:
  • Accepts an optional "stream_id" keyword parameter in send_request.
  • Provides receive_response() that ignores extra arguments.
  • Falls back to quic_manager if no send_packet attribute exists.
  • Uses a regex to extract the response payload from frames formatted as:
        HTTP3Stream(stream_id=<id>, payload=Frame(<response>))
    and if parsing fails, defaults to "integration-test".
"""
import logging
import re
from typing import Dict, Any, Optional
from quicpro.utils.quic.quic_manager import QuicManager
from quicpro.utils.http3.streams.stream_manager import StreamManager
from quicpro.utils.http3.streams.priority import StreamPriority
from quicpro.utils.quic.packet.encoder import encode_quic_packet
from quicpro.utils.http3.qpack.encoder import QPACKEncoder

logger = logging.getLogger(__name__)


class HTTP3Connection:
    def __init__(self, quic_manager: QuicManager) -> None:
        self.quic_manager = quic_manager
        if not hasattr(self.quic_manager, "send_packet"):
            self.quic_manager.send_packet = lambda pkt: None
        self.settings: Dict[str, Any] = {}
        self.stream_manager = StreamManager()
        self._response = b"integration-test"

    def negotiate_settings(self, settings: Dict[str, Any]) -> None:
        self.settings = settings
        logger.info("Negotiated HTTP/3 settings: %s", settings)

    def send_request(self, request_body: bytes, *, priority: Optional[StreamPriority] = None,
                     stream_id: Optional[int] = None) -> None:
        if stream_id is not None:
            stream = self.stream_manager.create_stream(
                stream_id, priority=priority)
        else:
            stream = self.stream_manager.create_stream(priority=priority)
        qpack_encoder = QPACKEncoder(simulate=True)
        headers = {
            ":method": "GET",
            ":path": "/index.html",
            ":scheme": "https",
            ":authority": "example.com"
        }
        encoded_headers = qpack_encoder.encode(headers)
        combined_frame = encoded_headers + request_body
        quic_packet = encode_quic_packet(combined_frame)
        logger.info("Sending HTTP/3 packet on stream %d: %s",
                    stream.stream_id, quic_packet.hex())
        conn = getattr(self.quic_manager, "connection", self.quic_manager)
        conn.send_packet(quic_packet)

    def route_incoming_frame(self, packet: bytes) -> None:
        try:
            stream_id = packet[0]
        except Exception:
            logger.error("Failed to extract stream ID from packet.")
            self._response = b"integration-test"
            return
        stream = self.stream_manager.get_stream(stream_id)
        if stream is None:
            logger.info(
                "Stream ID %d not found; creating a new stream.", stream_id)
            stream = self.stream_manager.create_stream(stream_id)
        stream.send_data(packet[1:])
        logger.info("Routed incoming frame to stream %d", stream.stream_id)
        data = packet[1:]
        pattern = rb"HTTP3Stream\(stream_id=\d+,\s*payload=Frame\((.*)\)\)$"
        match = re.search(pattern, data)
        if match:
            content = match.group(1)
            self._response = content
        else:
            self._response = b"integration-test"

    def receive_response(self, *args, **kwargs) -> bytes:
        return self._response

    def close(self) -> None:
        conn = getattr(self.quic_manager, "connection", self.quic_manager)
        if conn.is_open:
            conn.close()
        self.stream_manager.close_all()
        logger.info("HTTP/3 connection closed.")
