"""
TLS Encryptor Module
This module encrypts QUIC packets using one of two modes:
  - Demo mode: A simplified TLS-like encryption using AES-GCM.
  - Real mode: A production-ready TLS encryption branch which leverages a DTLS/TLS library.
    (In production, you would integrate a proper DTLS library or TLS 1.3 handshake mechanism.)
A parameter 'demo' (True/False) selects between these modes. In real mode, a DTLS
context must be provided.
"""
import logging
from typing import Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.model.tls_config import TLSConfig
from quicpro.exceptions.encryption_error import EncryptionError

logger = logging.getLogger(__name__)

class TLSEncryptor:
    def __init__(self, udp_sender: Any, config: TLSConfig, demo: bool = True, dtls_context: Optional[Any] = None) -> None:
        self.udp_sender = udp_sender
        self.config = config
        self.demo = demo
        self.dtls_context = dtls_context
        if self.demo:
            self.aesgcm = AESGCM(self.config.key)
            self._sequence_number = 0
        else:
            if self.dtls_context is None:
                raise EncryptionError("Real TLS encryption mode requires a DTLS/TLS context.")
            logger.info("Real TLS encryption mode activated.")

    def _compute_nonce(self) -> bytes:
        seq_bytes = self._sequence_number.to_bytes(12, byteorder="big")
        return bytes(iv_byte ^ seq_byte for iv_byte, seq_byte in zip(self.config.iv, seq_bytes))

    def encrypt(self, quic_packet: bytes) -> None:
        if self.demo:
            try:
                nonce = self._compute_nonce()
                ciphertext = self.aesgcm.encrypt(nonce, quic_packet, None)
                record = self._sequence_number.to_bytes(8, byteorder="big") + ciphertext
                logger.info("TLSEncryptor (demo) produced packet with sequence number %d", self._sequence_number)
                self.udp_sender.send(record)
            except Exception as e:
                logger.exception("TLSEncryptor demo encryption failed: %s", e)
                raise EncryptionError(f"Demo encryption failed: {e}") from e
            finally:
                self._sequence_number += 1
        else:
            try:
                encrypted_packet = self.dtls_context.encrypt(quic_packet)
                logger.info("TLSEncryptor (real) encrypted packet using DTLS context.")
                self.udp_sender.send(encrypted_packet)
            except Exception as e:
                logger.exception("TLSEncryptor real encryption failed: %s", e)
                raise EncryptionError(f"Real encryption failed: {e}") from e
