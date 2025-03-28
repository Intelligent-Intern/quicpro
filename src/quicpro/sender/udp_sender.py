"""
UDPSender module.
Transmits encrypted packets over UDP with retry logic and context management.
"""

import logging
import time
from typing import Any

from quicpro.exceptions import TransmissionError

logger = logging.getLogger(__name__)


class UDPSender:
    """
    Sends UDP packets via an underlying network object.
    """
    def __init__(self, network: Any, max_retries: int = 3, retry_delay: float = 0.5) -> None:
        self.network = network
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def send(self, encrypted_packet: bytes) -> int:
        """
        Send an encrypted packet with retry logic.
        Raises:
          TransmissionError: if all retries fail.
        """
        attempt = 0
        while attempt <= self.max_retries:
            try:
                bytes_sent = self.network.transmit(encrypted_packet)
                logger.info("Sent %d bytes on attempt %d", bytes_sent, attempt + 1)
                return bytes_sent
            except Exception as e:
                attempt += 1
                logger.exception("UDPSender failed on attempt %d: %s", attempt, e)
                if attempt > self.max_retries:
                    raise TransmissionError(
                        f"Failed after {self.max_retries} attempts: {e}"
                    ) from e
                time.sleep(self.retry_delay * attempt)
        raise RuntimeError("Unexpected end of UDPSender.send()")

    def __enter__(self) -> "UDPSender":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if hasattr(self.network, "close"):
            try:
                self.network.close()
                logger.info("Network resources closed successfully.")
            except Exception as e:
                logger.exception("Error closing network resources: %s", e)
