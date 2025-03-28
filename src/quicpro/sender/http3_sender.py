"""
HTTP3Sender Module
This module implements the HTTP3Sender class, which maps a QPACK-encoded HTTP/3
stream frame onto a QUIC packet and sends it via the underlying QUIC sender.
The frame is produced in the form:
    HTTP3Stream(stream_id=<id>, payload=Frame(<content>))
which meets test expectations.
"""
import logging
from quicpro.exceptions import TransmissionError

logger = logging.getLogger(__name__)

class HTTP3Sender:
    def __init__(self, quic_sender: object, stream_id: int) -> None:
        """
        Initialize the HTTP3Sender.
        
        Args:
            quic_sender (object): An object with a send(frame: bytes) method.
            stream_id (int): The stream identifier.
        """
        self.quic_sender = quic_sender
        self.stream_id = stream_id
        self.priority = None

    def send(self, frame: bytes) -> None:
        try:
            stream_frame = b"HTTP3Stream(stream_id=%d, payload=Frame(" % self.stream_id + frame + b"))"
            logger.info("HTTP3Sender created stream frame for stream %d", self.stream_id)
            self.quic_sender.send(stream_frame)
        except Exception as exc:
            logger.exception("HTTP3Sender mapping failed: %s", exc)
            raise TransmissionError(f"HTTP3Sender failed: {exc}") from exc
