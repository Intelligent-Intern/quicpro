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
"""

import logging
from typing import Dict, Any

from quicpro.src.quicpro.utils.quic.quic_manager import QuicManager
from quicpro.utils.http3.streams.stream_manager import StreamManager
from quicpro.utils.http3.streams.priority import StreamPriority
from quicpro.utils.quic.packet.encoder import encode_quic_packet
from quicpro.utils.http3.qpack.encoder import QPACKEncoder

logger = logging.getLogger(__name__)


class HTTP3Connection:
    """
    Provides HTTP/3-specific behavior over a QUIC connection.

    This class integrates stream management and priority scheduling into the
    HTTP/3 workflow. Outgoing requests are encapsulated in streams created via
    the StreamManager and header blocks are generated using QPACK.
    """
    def __init__(self, quic_manager: QuicManager) -> None:
        """
        Initialize the HTTP3Connection with an existing QuicManager instance.

        Args:
            quic_manager (QuicManager): The QUIC manager handling low-level packet
                                        transmission and reception.
        """
        self.quic_manager = quic_manager
        self.settings: Dict[str, Any] = {}
        self.stream_manager = StreamManager()

    def negotiate_settings(self, settings: Dict[str, Any]) -> None:
        """
        Negotiate HTTP/3 settings with the server.

        In a full implementation, this method would send a SETTINGS frame and
        wait for an acknowledgment.

        Args:
            settings (Dict[str, Any]): The desired HTTP/3 settings.
        """
        self.settings = settings
        logger.info("Negotiated HTTP/3 settings: %s", settings)

    def send_request(self, request_body: bytes,
                     priority: StreamPriority = None) -> None:
        """
        Send an HTTP/3 request using a new stream with QPACK-encoded headers.

        A stream is created via the StreamManager with an optional priority.
        A header block is generated using QPACKEncoder and concatenated with the
        request body. The resulting frame is encapsulated in a QUIC packet and
        sent over the underlying connection.

        Args:
            request_body (bytes): The body of the HTTP/3 request.
            priority (StreamPriority, optional): Priority to assign to the stream.
        """
        # Create a new stream with the given priority.
        stream = self.stream_manager.create_stream(priority=priority)

        # Generate a QPACK-encoded header block.
        qpack_encoder = QPACKEncoder()
        # In production, headers would be derived from the request.
        headers = {
            ":method": "GET",
            ":path": "/index.html",
            ":scheme": "https",
            ":authority": "example.com"
        }
        encoded_headers = qpack_encoder.encode(headers)

        # Combine the encoded header block with the request body.
        combined_frame = encoded_headers + request_body

        # Encapsulate the combined frame into a QUIC packet.
        quic_packet = encode_quic_packet(combined_frame)
        logger.info(
            "Sending HTTP/3 packet on stream %d: %s",
            stream.stream_id,
            quic_packet.hex()
        )
        self.quic_manager.connection.send_packet(quic_packet)

    def route_incoming_frame(self, packet: bytes) -> None:
        """
        Demultiplex an incoming QUIC packet and route the HTTP/3 frame
        to the appropriate stream.

        The stream ID is extracted from the frame. If the stream does not
        exist, a new stream is created.

        Args:
            packet (bytes): The raw QUIC packet containing the HTTP/3 frame.
        """
        try:
            # Placeholder extraction: assume the first byte represents the stream ID.
            stream_id = packet[0]
        except Exception:
            logger.error("Failed to extract stream ID from packet.")
            return

        stream = self.stream_manager.get_stream(stream_id)
        if not stream:
            logger.info("Stream ID %d not found; creating a new stream.", stream_id)
            stream = self.stream_manager.create_stream()
        # Route the remaining packet data (excluding the stream ID) to the stream.
        stream.send_data(packet[1:])
        logger.info("Routed incoming frame to stream %d", stream.stream_id)

    def close(self) -> None:
        """
        Close the HTTP/3 connection by shutting down the underlying QUIC
        connection and closing all managed streams.
        """
        if self.quic_manager.connection.is_open:
            self.quic_manager.connection.close()
        self.stream_manager.close_all()
        logger.info("HTTP/3 connection closed.")
