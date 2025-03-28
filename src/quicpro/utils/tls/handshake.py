"""
TLS Encryption Module (Production Ready)
Provides functions and classes to encrypt data using a negotiated TLSContext.
This module calls the underlying TLSContext.encrypt() method to perform the
actual encryption, and wraps it in a higher-level API for ease of use.
"""

import logging
from typing import Any
from .tls_context import TLSContext

logger = logging.getLogger(__name__)

def encrypt_data(tls_context: TLSContext, plaintext: bytes) -> bytes:
    """
    Encrypt the given plaintext using the provided TLSContext.

    Args:
        tls_context (TLSContext): An instance of TLSContext (e.g., TLS13Context or TLS12Context)
                                   that has completed the handshake and holds negotiated keys.
        plaintext (bytes): The plaintext data to encrypt.

    Returns:
        bytes: The resulting ciphertext.

    Raises:
        Exception: Propagates any exception raised during encryption.
    """
    try:
        ciphertext = tls_context.encrypt(plaintext)
        logger.debug("Data encrypted successfully (%d bytes plaintext)", len(plaintext))
        return ciphertext
    except Exception as e:
        logger.exception("Encryption failed")
        raise e

class TLSEncryptionEngine:
    """
    Encapsulates encryption operations for TLS contexts.
    
    This class abstracts the encryption process, allowing consumers to simply
    call the encrypt() method irrespective of the underlying TLS version.
    """
    def __init__(self, tls_context: TLSContext) -> None:
        """
        Initialize the encryption engine with a given TLSContext.

        Args:
            tls_context (TLSContext): A TLS context that has performed handshake.
        """
        self.tls_context = tls_context

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using the underlying TLS context.

        Args:
            data (bytes): Data to be encrypted.

        Returns:
            bytes: Encrypted data (ciphertext).

        Raises:
            Exception: Propagates errors from the TLSContext.encrypt() method.
        """
        return encrypt_data(self.tls_context, data)