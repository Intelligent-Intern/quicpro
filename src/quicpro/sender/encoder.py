"""
Encoder Module

Encodes a message into an HTTP/3 frame using QPACK for header encoding.
The encoded frame is then sent via an HTTP3Sender.
"""

import logging
from typing import Any, Union

from quicpro.exceptions.encoding_error import EncodingError
from quicpro.utils.http3.qpack.encoder import QPACKEncoder
from quicpro.model.message import Message

logger = logging.getLogger(__name__)


class Encoder:
    """
    Encodes a message into an HTTP/3 frame using QPACK for header block encoding.
    
    This encoder creates a QPACK-encoded header block containing the message content.
    The resulting frame is then passed to an HTTP3Sender for transmission.
    """
    def __init__(self, http3_sender: Any) -> None:
        """
        Initialize the Encoder with an HTTP3Sender instance.
        
        Args:
            http3_sender (Any): An instance of HTTP3Sender used to send the frame.
        """
        self.http3_sender = http3_sender
        self.qpack_encoder = QPACKEncoder()

    def encode(self, message: Union[Message, str, dict]) -> None:
        """
        Encode the provided message into an HTTP/3 frame and send it via the HTTP3Sender.
        
        The message is converted to a Message instance if necessary, and a header block
        is generated using QPACKEncoder. In this simple example, the header block includes
        a single header field "content" carrying the message content.
        
        Args:
            message (Union[Message, str, dict]): The message to encode.
        
        Raises:
            EncodingError: If encoding fails.
        """
        try:
            if isinstance(message, Message):
                msg = message
            elif isinstance(message, dict):
                msg = Message(**message)
            else:
                msg = Message(content=message)
            # Construct headers with the message content.
            headers = {
                "content": msg.content,
                # Additional headers (e.g., ":method", ":path") could be added here.
            }
            # Generate a QPACK-encoded header block.
            encoded_headers = self.qpack_encoder.encode(headers)
            # In this simple example, the frame consists solely of the encoded header block.
            frame = encoded_headers
            logger.info("Encoder produced frame: %s", frame)
            self.http3_sender.send(frame)
        except Exception as e:
            logger.exception("Encoding failed: %s", e)
            raise EncodingError(f"Encoding failed: {e}") from e
