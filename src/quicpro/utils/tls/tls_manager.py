"""
TLS Manager Module (Production Ready)
Provides a unified interface for TLS operations including handshake,
encryption, decryption, and key updates. It automatically selects between
TLS 1.3 and TLS 1.2 contexts based on the provided configuration.
"""

import socket
import logging
from typing import Optional

from .tls_context import TLSContext
from .tls13_context import TLS13Context
from .tls12_context import TLS12Context
from .handshake import TLSHandshake, perform_tls_handshake
from .encryption import TLSEncryptionEngine, encrypt_data
from .decryption import TLSDecryptionEngine, decrypt_data
from .certificates import load_certificate, load_private_key, verify_certificate
from .base import log_tls_debug

logger = logging.getLogger(__name__)

class TLSManager:
    def __init__(self, version: str, certfile: str, keyfile: str, cafile: Optional[str] = None) -> None:
        """
        Initialize the TLS Manager with the desired TLS version.
        
        Args:
            version (str): TLS version required; should be either "TLSv1.3" or "TLSv1.2".
            certfile (str): Path to the certificate file.
            keyfile (str): Path to the private key file.
            cafile (Optional[str]): Optional CA bundle for certificate verification.
        """
        if version == "TLSv1.3":
            self.tls_context: TLSContext = TLS13Context(certfile, keyfile, cafile)
        elif version == "TLSv1.2":
            self.tls_context: TLSContext = TLS12Context(certfile, keyfile, cafile)
        else:
            raise ValueError("Unsupported TLS version. Use 'TLSv1.3' or 'TLSv1.2'.")
        
        self.handshake = TLSHandshake(self.tls_context)
        self.encryption_engine = TLSEncryptionEngine(self.tls_context)
        self.decryption_engine = TLSDecryptionEngine(self.tls_context)
        log_tls_debug(f"TLSManager initialized with version {version}")

    def perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        """
        Perform the TLS handshake over the provided socket.
        
        Args:
            sock (socket.socket): A connected socket.
            server_hostname (str): The SNI hostname.
        """
        log_tls_debug("Performing TLS handshake via TLSManager")
        self.handshake.start(sock, server_hostname)
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt the provided data using the negotiated TLS keys.
        
        Args:
            data (bytes): Plaintext data.
            
        Returns:
            bytes: Encrypted ciphertext.
        """
        log_tls_debug("Encrypting data via TLSManager")
        return self.encryption_engine.encrypt(data)
    
    def decrypt_data(self, data: bytes) -> bytes:
        """
        Decrypt the provided data using the negotiated TLS keys.
        
        Args:
            data (bytes): Ciphertext data.
            
        Returns:
            bytes: Decrypted plaintext.
        """
        log_tls_debug("Decrypting data via TLSManager")
        return self.decryption_engine.decrypt(data)
    
    def update_keys(self) -> None:
        """
        Update (rotate) the negotiated TLS keys.
        """
        log_tls_debug("Updating TLS keys via TLSManager")
        self.tls_context.update_keys()