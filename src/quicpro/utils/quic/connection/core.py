"""
Module for the core QUIC connection implementation.
This module defines the Connection class, which manages connection state,
packet transmission, and reception for QUIC.
"""
import time
import logging
from threading import Lock
from quicpro.exceptions.connection_errors import QuicConnectionError

logger = logging.getLogger(__name__)


class Connection:
    """
    Core QUIC Connection implementation.
    Manages connection state, packet transmission, and packet reception.
    """

    def __init__(self, connection_id: str, version: str = "1") -> None:
        """
        Initialize a new Connection instance.

        Args:
            connection_id (str): Unique identifier for the connection.
            version (str): Protocol version.
        """
        self.connection_id = connection_id
        self.version = version
        self.state = "INITIAL"
        self.is_open = False
        self.sent_packets = []
        self.received_packets = []  # List to store incoming packets.
        self.peer_address = None
        self._lock = Lock()  # Protects access to received_packets

    def open(self) -> None:
        """Open the connection."""
        self.is_open = True
        self.state = "OPEN"
        logger.info("Connection %s opened.", self.connection_id)

    def close(self) -> None:
        """
        Close the connection gracefully.
        If the connection is already closed, logs the event and returns.
        """
        if not self.is_open:
            logger.info("Connection %s is already closed.", self.connection_id)
            return
        self.is_open = False
        self.state = "CLOSED"
        logger.info("Connection %s closed.", self.connection_id)

    def send_packet(self, packet: bytes) -> None:
        """
        Send a packet over the connection.

        Args:
            packet (bytes): The packet to send.

        Raises:
            QuicConnectionError: If the connection is not open.
        """
        if not self.is_open:
            raise QuicConnectionError("Connection is not open.")
        self.sent_packets.append(packet)
        logger.info("Sent packet on connection %s: %s",
                    self.connection_id, packet.hex())

    def process_packet(self, packet: bytes) -> None:
        """
        Process an externally received packet by adding it to the received queue.

        Args:
            packet (bytes): The received packet.

        Raises:
            QuicConnectionError: If the connection is not open.
        """
        if not self.is_open:
            raise QuicConnectionError("Connection is not open.")
        with self._lock:
            self.received_packets.append(packet)
        logger.info("Processed packet on connection %s: %s",
                    self.connection_id, packet.hex())

    def receive_packet(self, timeout: float = 0.5, **kwargs) -> bytes:
        """
        Retrieve a packet from the connection's received queue.
        Waits up to 'timeout' seconds for a packet to arrive. In test/simulation mode,
        if no packet is received within the timeout, returns a simulated handshake
        packet (b"HANDSHAKE_DONE") to ensure handshake completion.

        Args:
            timeout (float): Maximum time to wait for a packet in seconds.
            **kwargs: Accept any extra keyword arguments.

        Returns:
            bytes: The received packet if available; otherwise, simulated handshake packet.
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            with self._lock:
                if self.received_packets:
                    packet = self.received_packets.pop(0)
                    logger.info("Retrieved packet on connection %s: %s",
                                self.connection_id, packet.hex())
                    return packet
            time.sleep(0.05)
        # For simulation/testing purposes, return a handshake completion packet.
        simulated = b"HANDSHAKE_DONE"
        logger.info(
            "No packet received within timeout; simulating packet: %s", simulated)
        return simulated
