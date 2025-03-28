import logging
from typing import Any
from quicpro.exceptions import DecodingError

logger = logging.getLogger(__name__)


class Decoder:
    """Decoder class to decode QUIC packets."""

    def __init__(self, consumer_app: Any) -> None:
        """Initialize the Decoder with a consumer application."""
        self.consumer_app = consumer_app

    def decode(self, quic_packet: bytes) -> None:
        """Decode the given QUIC packet and pass the message to the consumer app."""
        try:
            frame_prefix = b"Frame("
            start_index = quic_packet.find(frame_prefix)
            if start_index != -1:
                start_index += len(frame_prefix)
                end_index = quic_packet.find(b")", start_index)
                if end_index != -1:
                    message_content = quic_packet[start_index:end_index].decode(
                        "utf-8")
                else:
                    logger.warning(
                        "Closing delimiter not found; defaulting to 'Unknown'.")
                    message_content = "Unknown"
            else:
                logger.warning(
                    "Frame prefix not found; defaulting to 'Unknown'.")
                message_content = "Unknown"
            logger.info("Decoder extracted message: %s", message_content)
            self.consumer_app.consume(message_content)
        except Exception as exc:
            logger.exception("Decoder encountered an error: %s", exc)
            raise DecodingError(f"Error decoding quic packet: {exc}") from exc

    def consume(self, message: str) -> None:
        """Consume the provided message using the consumer app."""
        self.consumer_app.consume(message)

