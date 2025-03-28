"""
Encoder module.
Encodes a message into a binary frame and sends it via an HTTP3Sender.
"""

import logging
from typing import Any

from pydantic import BaseModel
from quicpro.exceptions import EncodingError

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Message model."""
    content: str


class Encoder:
    """
    Encodes a message into a frame.
    """
    def __init__(self, http3_sender: Any) -> None:
        self.http3_sender = http3_sender

    def encode(self, message: Message) -> None:
        """
        Encode the message and send via HTTP3Sender.
        Raises:
          EncodingError: on failure.
        """
        try:
            encoded_frame = f"Frame({message.content})".encode("utf-8")
            logger.info("Encoder produced frame: %s", encoded_frame)
            self.http3_sender.send(encoded_frame)
        except Exception as e:
            logger.exception("Encoding failed: %s", e)
            raise EncodingError(f"Encoding failed: {e}") from e
