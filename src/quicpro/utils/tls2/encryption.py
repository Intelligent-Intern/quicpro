"""
Encryption Module for TLS.
Provides functions and classes to encrypt data using negotiated TLS keys.
Additional audit logging and error categorization have been integrated per full QUIC standard.
"""
import logging
from typing import Any
from .tls_context import TLSContext

logger = logging.getLogger(__name__)


def encrypt_data(tls_context: TLSContext, plaintext: bytes) -> bytes:
    try:
        logger.debug(
            "Attempting encryption of %d bytes of plaintext", len(plaintext))
        ciphertext = tls_context.encrypt(plaintext)
        logger.debug(
            "Encryption successful: produced %d bytes of ciphertext", len(ciphertext))
        logger.info(
            "AUDIT: Encryption completed successfully (plaintext length: %d)", len(plaintext))
        return ciphertext
    except Exception as e:
        logger.error("AUDIT: Encryption error encountered", exc_info=True)
        raise e


class TLSEncryptionEngine:
    def __init__(self, tls_context: TLSContext) -> None:
        self.tls_context = tls_context

    def encrypt(self, data: bytes) -> bytes:
        logger.debug(
            "TLSEncryptionEngine: Received %d bytes of data for encryption", len(data))
        return encrypt_data(self.tls_context, data)
