"""
TLSDecryptor module.
Decrypts incoming AES-GCM encrypted UDP datagrams and passes the decrypted QUIC packet to a QUICReceiver.
"""

import logging
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.model.tls_config import TLSConfig
from quicpro.exceptions import DecryptionError

logger = logging.getLogger(__name__)


class TLSDecryptor:
    """
    TLSDecryptor decrypts AES-GCM encrypted UDP datagrams and passes the decrypted packet to a QUICReceiver.
    """
    def __init__(self, quic_receiver: Any, config: TLSConfig) -> None:
        """
        Args:
          quic_receiver: An object with a receive(packet: bytes) method.
          config: TLSConfig containing the encryption key and IV.
        """
        self.quic_receiver = quic_receiver
        self.config = config
        self.aesgcm = AESGCM(self.config.key)

    def _compute_nonce(self, seq_number: int) -> bytes:
        """
        Compute the per-record nonce.
        """
        seq_bytes = seq_number.to_bytes(12, byteorder='big')
        return bytes(iv_byte ^ seq_byte for iv_byte, seq_byte in zip(self.config.iv, seq_bytes))

    def decrypt(self, encrypted_packet: bytes) -> None:
        """
        Decrypt an encrypted UDP datagram and pass the decrypted QUIC packet to the receiver.
        Raises:
          DecryptionError: if decryption fails.
        """
        try:
            if len(encrypted_packet) < 9:
                raise ValueError("Encrypted packet is too short.")
            seq_number = int.from_bytes(encrypted_packet[:8], byteorder='big')
            ciphertext = encrypted_packet[8:]
            nonce = self._compute_nonce(seq_number)
            quic_packet = self.aesgcm.decrypt(nonce, ciphertext, None)
            logger.info("Decrypted packet with sequence number %d", seq_number)
            self.quic_receiver.receive(quic_packet)
        except Exception as exc:
            logger.exception("TLSDecryptor decryption failed: %s", exc)
            raise DecryptionError(f"Decryption failed: {exc}") from exc
