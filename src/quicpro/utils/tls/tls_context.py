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
        pass

    @abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        pass

    @abstractmethod
    def update_keys(self) -> None:
        pass
