"""
HTTP3Sender Module

This module implements the HTTP3Sender class, which maps a QPACK-encoded HTTP/3
stream frame onto a QUIC packet and sends it via the underlying QUICSender.
It also integrates stream priority by embedding the priority value in the frame.
"""

import logging
from typing import Any, Optional

from quicpro.exceptions import TransmissionError

logger = logging.getLogger(__name__)


class HTTP3Sender:
    """
    Maps an encoded HTTP/3 frame onto a QUIC packet and sends it via the QUICSender.

    The frame is constructed by combining:
      - The stream ID (1 byte for simplicity)
      - An optional priority byte (if a StreamPriority is assigned)
      - The QPACK-encoded HTTP/3 header block and request body.
    """
    def __init__(self, quic_sender: Any, stream_id: int) -> None:
        """
        Initialize the HTTP3Sender.

        Args:
            quic_sender (Any): The underlying QUICSender instance.
            stream_id (int): The identifier of the HTTP/3 stream.
        """
        self.quic_sender = quic_sender
        self.stream_id = stream_id
        self.priority: Optional[Any] = None

    def send(self, frame: bytes) -> None:
        """
        Create an HTTP/3 stream frame and send it using the QUICSender.

        The stream frame is constructed by combining:
          - The stream ID (encoded in 1 byte)
          - An optional priority byte (if assigned)
          - The frame payload (QPACK-encoded header block and body)

        Args:
            frame (bytes): The QPACK-encoded HTTP/3 frame.

        Raises:
            TransmissionError: If sending fails.
        """
        try:
            # Encode stream ID as 1 byte.
            header = self.stream_id.to_bytes(1, byteorder="big")
            if self.priority is not None:
                # Encode priority weight as 1 byte.
                prio_byte = self.priority.weight.to_bytes(1, byteorder="big")
                stream_frame = header + prio_byte + frame
            else:
                stream_frame = header + frame
            logger.info("HTTP3Sender created stream frame for stream %d",
                        self.stream_id)
            self.quic_sender.send(stream_frame)
        except Exception as exc:
            logger.exception("HTTP3Sender mapping failed: %s", exc)
            raise TransmissionError(f"HTTP3Sender failed: {exc}") from exc
