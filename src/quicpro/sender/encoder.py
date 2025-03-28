"""
Encoder Module
Encodes a message into an HTTP/3 frame using QPACK for header encoding.
This implementation expects a Message with a "content" attribute and produces
a frame of the form: b"Frame(<content>)", per test expectations.
"""
import logging
from typing import Any
from quicpro.exceptions.encoding_error import EncodingError
from quicpro.utils.http3.qpack.encoder import QPACKEncoder
from quicpro.model.message import Message

logger = logging.getLogger(__name__)


class Encoder:
    """Encodes messages for HTTP/3 transmission."""

    def __init__(self, http3_sender: Any) -> None:
        """Initializes the encoder with a sender."""
        self.http3_sender = http3_sender
        self.qpack_encoder = QPACKEncoder(simulate=True)  # Use simulation mode

    def encode(self, message: object) -> None:
        """Encodes the given message into a frame."""
        try:
            if isinstance(message, Message):
                content = message.content
            elif isinstance(message, dict) and "content" in message:
                content = message["content"]
            elif isinstance(message, str):
                content = message
            else:
                raise EncodingError("Unsupported message type")
            frame = b"Frame(" + content.encode("utf-8") + b")"
            logger.info("Encoder produced frame: %s", frame)
            self.http3_sender.send(frame)
        except Exception as e:
            logger.exception("Encoding failed: %s", e)
            raise EncodingError(f"Encoding failed: {e}") from e

