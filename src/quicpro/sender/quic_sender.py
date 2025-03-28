"""
QUICSender module.
Packages HTTP/3 stream frames into QUIC packets and sends them using the TLSEncryptor.
"""
import logging
from typing import Any
from quicpro.exceptions import TransmissionError
from quicpro.utils.quic.packet.encoder import encode_quic_packet

logger = logging.getLogger(__name__)


class QUICSender:
    """
    Encapsulates an HTTP/3 stream frame into a QUIC packet.
    """

    def __init__(self, tls_encryptor: Any) -> None:
        self.tls_encryptor = tls_encryptor

    def send(self, stream_frame: bytes) -> None:
        """
        Package and send the provided HTTP/3 stream frame.
        Raises:
          TransmissionError: if packaging or sending fails.
        """
        try:
            quic_packet = encode_quic_packet(stream_frame)
            logger.info("QUICSender packaged packet: %s", quic_packet)
            self.tls_encryptor.encrypt(quic_packet)
        except Exception as e:
            logger.exception("QUICSender packaging failed: %s", e)
            raise TransmissionError(f"Transmission error: {e}") from e

    def close(self) -> None:
        """
        Close the sender and perform any necessary cleanup.
        """
        logger.info("QUICSender is closing.")

