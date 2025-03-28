"""
Abstract TLS Context Module

This module defines the abstract base class for TLS context implementations.
Implementations must provide methods for handshake, encryption, decryption,
and key updates.
"""

from abc import ABC, abstractmethod

class TLSContext(ABC):
    """
    Abstract Base Class for TLS contexts.
    
    Defines the interface for:
      - Performing the TLS handshake.
      - Encrypting data using negotiated keys.
      - Decrypting data using negotiated keys.
      - Updating or rotating keys.
    """

    @abstractmethod
    def perform_handshake(self, sock, server_hostname: str) -> None:
        """
        Perform the TLS handshake over the given socket.

        Args:
            sock: A connected socket instance.
            server_hostname (str): The hostname for server name indication (SNI).
        """
        pass

    @abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt the provided plaintext using the negotiated cipher suite.

        Args:
            plaintext (bytes): The data to encrypt.

        Returns:
            bytes: The encrypted ciphertext.
        """
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt the provided ciphertext using the negotiated cipher suite.

        Args:
            ciphertext (bytes): The data to decrypt.

        Returns:
            bytes: The decrypted plaintext.
        """
        pass

    @abstractmethod
    def update_keys(self) -> None:
        """
        Update or rotate the encryption keys according to the TLS specifications.
        """
        pass