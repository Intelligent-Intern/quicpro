"""
QuicManager module.
Integrates connection, header, stream, packet operations and manages a synchronous event loop.
"""

import threading
import logging

from quicpro.utils.quic.connection.core import Connection
from quicpro.utils.quic.header.header import Header
from quicpro.utils.quic.packet.encoder import encode_quic_packet
from quicpro.utils.quic.packet.decoder import decode_quic_packet
from quicpro.utils.quic.streams.manager import StreamManager
from quicpro.utils.event_loop.sync_loop import SyncEventLoop

logger = logging.getLogger(__name__)


class QuicManager:
    """
    Manages QUIC communications.
    """
    def __init__(self, connection_id: str, header_fields: dict, event_loop_max_workers: int = 4) -> None:
        self.connection = Connection(connection_id)
        self.connection.open()  # Ensure the connection is open
        self.header = Header(**header_fields)
        self.stream_manager = StreamManager()
        self.event_loop = SyncEventLoop(max_workers=event_loop_max_workers)
        self._event_loop_thread = None
        self._start_event_loop()

    def _start_event_loop(self) -> None:
        """Start the synchronous event loop in a daemon thread."""
        self._event_loop_thread = threading.Thread(target=self.event_loop.run_forever, daemon=True)
        self._event_loop_thread.start()

    def send_stream(self, stream_id: int, stream_frame: bytes) -> None:
        """
        Encapsulate the stream_frame with header information and send via connection.
        """
        header_bytes = self.header.encode()
        combined_frame = header_bytes + stream_frame
        quic_packet = encode_quic_packet(combined_frame)
        logger.info("QuicManager sending packet: %s", quic_packet.hex())
        self.connection.send_packet(quic_packet)

    def receive_packet(self, packet: bytes) -> None:
        """
        Process an incoming QUIC packet.
        """
        try:
            combined_frame = decode_quic_packet(packet)
            header = Header.decode(combined_frame)
            header_encoded = header.encode()
            stream_frame = combined_frame[len(header_encoded):]
            logger.info("QuicManager received header: %s", header)
            logger.info("QuicManager received stream frame: %s", stream_frame)
            stream_id_val = int(header.fields.get("stream_id", 0))
            stream = self.stream_manager.get_stream(stream_id_val)
            if not stream:
                stream = self.stream_manager.create_stream(stream_id_val)
            stream.send_data(stream_frame)
        except Exception as e:
            logger.exception("QuicManager failed to process incoming packet: %s", e)

    def close(self) -> None:
        """
        Close the connection, stop the event loop, and join the loop thread.
        """
        if self.connection.is_open:
            self.connection.close()
        self.event_loop.stop()
        if self._event_loop_thread:
            self._event_loop_thread.join()
