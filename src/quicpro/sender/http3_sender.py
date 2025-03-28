"""
HTTP3Sender module.
Maps an encoded frame onto an HTTP/3 stream and sends it using the QUICSender.
"""

import logging
from typing import Any

from quicpro.exceptions import TransmissionError

logger = logging.getLogger(__name__)


class HTTP3Sender:
    """
    Maps a frame to an HTTP/3 stream frame.
    """
    def __init__(self, quic_sender: Any, stream_id: int) -> None:
        self.quic_sender = quic_sender
        self.stream_id = stream_id

    def send(self, frame: bytes) -> None:
        """
        Create an HTTP/3 stream frame from the encoded frame and send it.
        Raises:
          TransmissionError: if sending fails.
        """
        try:
            stream_frame = b"HTTP3Stream(stream_id=%d, payload=" % self.stream_id + frame + b")"
            logger.info("HTTP3Sender created stream frame: %s", stream_frame)
            self.quic_sender.send(stream_frame)
        except Exception as e:
            logger.exception("HTTP3Sender mapping failed: %s", e)
            raise TransmissionError(f"HTTP3Sender failed: {e}") from e
