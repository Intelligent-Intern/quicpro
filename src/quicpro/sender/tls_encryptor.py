"""
TLSEncryptor module.
Encrypts QUIC packets using AES-GCM and sends them via UDPSender.
"""

import logging
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.model.tls_config import TLSConfig
from quicpro.exceptions import EncryptionError

logger = logging.getLogger(__name__)


class TLSEncryptor:
    """
    Encrypts a QUIC packet using AES-GCM, prepending a sequence number.
    """
    def __init__(self, udp_sender: Any, config: TLSConfig) -> None:
        self.udp_sender = udp_sender
        self.config = config
        self.aesgcm = AESGCM(self.config.key)
        self._sequence_number = 0

    def _compute_nonce(self) -> bytes:
        seq_bytes = self._sequence_number.to_bytes(12, byteorder='big')
        return bytes(iv_byte ^ seq_byte for iv_byte, seq_byte in zip(self.config.iv, seq_bytes))

    def encrypt(self, quic_packet: bytes) -> None:
        """
        Encrypt the given QUIC packet and send it.
        Raises:
          EncryptionError: if encryption or transmission fails.
        """
        try:
            nonce = self._compute_nonce()
            ciphertext = self.aesgcm.encrypt(nonce, quic_packet, None)
            record = self._sequence_number.to_bytes(8, byteorder='big') + ciphertext
            logger.info("TLSEncryptor produced packet with sequence number %d", self._sequence_number)
            self.udp_sender.send(record)
        except Exception as e:
            logger.exception("TLSEncryptor encryption failed: %s", e)
            raise EncryptionError(f"Encryption failed: {e}") from e
        finally:
            self._sequence_number += 1
