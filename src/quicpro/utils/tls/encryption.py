"""
Encryption Module for TLS.
Provides functions and classes to encrypt data using negotiated TLS keys.
"""

def encrypt_data(tls_context, plaintext: bytes) -> bytes:
    """
    Encrypt the given plaintext using the provided TLSContext.
    """
    # Call tls_context.encrypt()
    return tls_context.encrypt(plaintext)

class TLSEncryptionEngine:
    """
    Encapsulate encryption-related operations for TLS.
    """
    def __init__(self, tls_context):
        self.tls_context = tls_context

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using the TLS context."""
        return encrypt_data(self.tls_context, data)
