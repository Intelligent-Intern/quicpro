"""
Module for the core QUIC connection implementation.

This module defines the Connection class, which manages connection state,
packet transmission, and reception for QUIC.
"""

import logging
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
        self.received_packets = []
        self.peer_address = None

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

    def receive_packet(self, packet: bytes) -> None:
        """
        Process a received packet.

        Args:
            packet (bytes): The received packet.

        Raises:
            QuicConnectionError: If the connection is not open.
        """
        if not self.is_open:
            raise QuicConnectionError("Connection is not open.")
        self.received_packets.append(packet)
        logger.info("Received packet on connection %s: %s",
                    self.connection_id, packet.hex())
