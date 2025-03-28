"""
Network module.
Handles low-level UDP socket operations.
"""

import socket
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class Network:
    """
    Handles network operations for sending UDP datagrams.
    """
    def __init__(self, remote_address: Tuple[str, int], timeout: float = 5.0) -> None:
        self.remote_address = remote_address
        self.timeout = timeout
        self.socket = self._setup_socket()

    def _setup_socket(self) -> socket.socket:
        """Creates and configures a UDP socket."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            logger.info("UDP socket created with timeout %s seconds", self.timeout)
            return sock
        except Exception as exc:
            logger.exception("Failed to create UDP socket: %s", exc)
            raise

    def transmit(self, data: bytes) -> int:
        """
        Send data via UDP.
        """
        try:
            bytes_sent = self.socket.sendto(data, self.remote_address)
            logger.info("Transmitted %d bytes to %s", bytes_sent, self.remote_address)
            return bytes_sent
        except Exception as exc:
            logger.exception("Network transmission failed: %s", exc)
            raise

    def close(self) -> None:
        """Close the UDP socket."""
        try:
            if self.socket:
                self.socket.close()
                logger.info("UDP socket closed")
        except Exception as exc:
            logger.exception("Error closing UDP socket: %s", exc)
            raise
