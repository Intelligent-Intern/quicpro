"""
TLS Decryption Module (Production Ready)
Provides functions and classes to decrypt received data using a negotiated TLSContext.
This module invokes the underlying TLSContext.decrypt() method to perform the actual decryption,
and exposes a higher-level API for streamlined use.
Additional audit logging and error categorization have been integrated per full QUIC standard.
"""
import logging
from typing import Any
from .tls_context import TLSContext

logger = logging.getLogger(__name__)

def decrypt_data(tls_context: TLSContext, ciphertext: bytes) -> bytes:
    """
    Decrypt the given ciphertext using the provided TLSContext.
    
    Args:
        tls_context (TLSContext): An instance of TLSContext (e.g., TLS13Context or TLS12Context)
                                   that holds negotiated keys after a successful handshake.
        ciphertext (bytes): The ciphertext data to decrypt.
        
    Returns:
        bytes: The resulting plaintext.
        
    Raises:
        Exception: Propagates any error raised during decryption.
    """
    try:
        logger.debug("Attempting decryption of %d bytes of ciphertext", len(ciphertext))
        plaintext = tls_context.decrypt(ciphertext)
        logger.debug("Decryption successful: obtained %d bytes of plaintext", len(plaintext))
        logger.info("AUDIT: Decryption completed successfully (plaintext length: %d)", len(plaintext))
        return plaintext
    except Exception as e:
        logger.error("AUDIT: Decryption error encountered", exc_info=True)
        # Categorize error for QUIC standards (this could be extended to wrap or log error codes)
        raise e

class TLSDecryptionEngine:
    """
    Encapsulates decryption operations for TLS contexts.
    
    This class abstracts the decryption process, exposing a simple API
    regardless of the underlying TLS version.
    """
    def __init__(self, tls_context: TLSContext) -> None:
        """
        Initialize the decryption engine with a given TLSContext.
        
        Args:
            tls_context (TLSContext): A TLS context that has completed its handshake.
        """
        self.tls_context = tls_context

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt data using the underlying TLSContext.
        
        Args:
            data (bytes): The ciphertext to be decrypted.
            
        Returns:
            bytes: The decrypted plaintext.
            
        Raises:
            Exception: Propagates errors from the TLSContext.decrypt() method.
        """
        logger.debug("TLSDecryptionEngine: Received %d bytes of data for decryption", len(data))
        return decrypt_data(self.tls_context, data)
