"""
QuicManager module (Production Ready)

Integrates connection, header, stream, packet operations and manages a synchronous event loop.
This version fully integrates the QUIC handshake, version negotiation, congestion control,
ACK/loss detection, and retransmission management.
"""

import threading
import logging
import time
from typing import Optional

from quicpro.utils.quic.connection.core import Connection
from quicpro.utils.quic.header.header import Header
from quicpro.utils.quic.packet.encoder import encode_quic_packet
from quicpro.utils.quic.packet.decoder import decode_quic_packet
from quicpro.utils.quic.streams.manager import StreamManager
from quicpro.utils.event_loop.sync_loop import SyncEventLoop

# Integrated handshake and negotiation
from quicpro.utils.quic.handshake_and_negotiation import QUICHandshake

# Congestion control and retransmission management
from quicpro.utils.quic.congestion_control import CongestionController, RetransmissionManager

logger = logging.getLogger(__name__)


class QuicManager:
    """
    Manages QUIC communications including handshake, packet encoding/decoding,
    stream management, congestion control, and loss recovery.
    """

    def __init__(self,
                 connection_id: str,
                 header_fields: dict,
                 event_loop_max_workers: int = 4,
                 handshake_timeout: float = 5.0) -> None:
        # Set up low-level connection and header.
        self.connection = Connection(connection_id)
        self.connection.open()  # Ensure the connection is open.
        self.header = Header(**header_fields)
        self.stream_manager = StreamManager()

        # Start the event loop.
        self.event_loop = SyncEventLoop(max_workers=event_loop_max_workers)
        self._event_loop_thread = threading.Thread(
            target=self.event_loop.run_forever, daemon=True)
        self._event_loop_thread.start()

        # Set up QUIC handshake and version negotiation.
        self.handshake = QUICHandshake(self.connection, local_version="v1")
        self._perform_handshake(handshake_timeout)

        # Initialize congestion control and retransmission manager.
        self.congestion_controller = CongestionController()
        self.rtx_manager = RetransmissionManager(self.congestion_controller)

        # Launch a separate thread to process retransmissions.
        self._retransmission_thread = threading.Thread(
            target=self._process_retransmissions_loop, daemon=True)
        self._retransmission_thread.start()

    def _perform_handshake(self, timeout: float) -> None:
        """Run the handshake state machine until completion or timeout."""
        start_time = time.time()
        self.handshake.send_initial_packet()
        while self.handshake.state != self.handshake.__class__.COMPLETED:
            if (time.time() - start_time) > timeout:
                raise TimeoutError("QUIC handshake timed out.")
            # In production, packets would be received from the network.
            packet = self.connection.receive_packet(timeout=0.5)
            if packet:
                self.handshake.process_incoming_packet(packet)
            else:
                # Retransmit if no response.
                self.handshake.send_initial_packet()
        logger.info(
            "QUIC handshake and version negotiation completed successfully.")

    def send_stream(self, stream_id: int, stream_frame: bytes) -> None:
        """
        Encapsulate the stream_frame with header information, store it for retransmission,
        and send the QUIC packet via the connection.
        """
        header_bytes = self.header.encode()
        combined_frame = header_bytes + stream_frame
        quic_packet = encode_quic_packet(combined_frame)

        # Register the packet with the retransmission manager.
        packet_number = self.rtx_manager.add_packet(quic_packet)
        logger.info("Sending QUIC packet, packet_number=%d, data=%s",
                    packet_number, quic_packet.hex())

        # Use congestion control: allow sending if permitted.
        if self.congestion_controller.can_send(len(quic_packet)):
            self.connection.send_packet(quic_packet)
        else:
            logger.warning(
                "Congestion window too small; packet queued for later transmission.")

    def receive_packet(self, packet: bytes) -> None:
        """
        Process an incoming QUIC packet.
        If the packet contains an acknowledgment frame, update congestion control
        and mark the corresponding packet as acknowledged.
        Otherwise, extract the stream-frame and deliver it to the appropriate stream.
        """
        try:
            combined_frame = decode_quic_packet(packet)
            header = Header.decode(combined_frame)
            header_encoded = header.encode()
            stream_frame = combined_frame[len(header_encoded):]
            logger.info("Received packet with header: %s", header)

            # Example: if ACK flag is set in header, process ACK.
            if header.fields.get("ack") == "1":
                pkt_num = int(header.fields.get("packet_number", -1))
                if pkt_num != -1:
                    self.rtx_manager.mark_acknowledged(pkt_num)
                    self.congestion_controller.on_ack(len(packet))
                    logger.info("Processed ACK for packet %d", pkt_num)
            else:
                # Normal processing: deliver stream_frame to the corresponding stream.
                stream_id_val = int(header.fields.get("stream_id", 0))
                stream = self.stream_manager.get_stream(stream_id_val)
                if not stream:
                    stream = self.stream_manager.create_stream(stream_id_val)
                stream.send_data(stream_frame)
        except Exception as e:
            logger.exception("Failed to process received packet: %s", e)

    def _process_retransmissions_loop(self):
        """
        Continuous loop that checks for timed-out packets and retransmits them.
        """
        while self.connection.is_open:
            time.sleep(0.1)
            self.rtx_manager.process_timeouts(timeout_interval=0.5)
            retrans_packets = self.rtx_manager.get_retransmission_packets()
            for pkt_num, packet in retrans_packets:
                logger.info("Retransmitting packet %d", pkt_num)
                self.connection.send_packet(packet)

    def close(self) -> None:
        """
        Close the QUIC connection, stop the event loop, and join all threads.
        """
        if self.connection.is_open:
            self.connection.close()
        self.event_loop.stop()
        if self._event_loop_thread:
            self._event_loop_thread.join()
        # The retransmission thread will exit once the connection is closed.
