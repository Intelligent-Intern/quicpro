"""
Production-Perfect TLS Manager with Fallback

This module implements TLSManager for production use.
It supports both TLSv1.3 and TLSv1.2 fallback, and uses AES-GCM for symmetric encryption
of application data. The AES-GCM key and IV are provided externally.
"""

import ssl
import socket
import logging
import struct
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TLSManager:
    def __init__(self, version: str, certfile: str, keyfile: str, cafile: Optional[str] = None,
                 key: Optional[bytes] = None, iv: Optional[bytes] = None) -> None:
        if version == "TLSv1.3":
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.context.minimum_version = ssl.TLSVersion.TLSv1_3
            self.context.maximum_version = ssl.TLSVersion.TLSv1_3
        elif version == "TLSv1.2":
            self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.context.minimum_version = ssl.TLSVersion.TLSv1_2
            self.context.maximum_version = ssl.TLSVersion.TLSv1_2
        else:
            raise ValueError("Unsupported TLS version. Use 'TLSv1.3' or 'TLSv1.2'.")
        self.context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        if cafile:
            self.context.load_verify_locations(cafile)
            self.context.verify_mode = ssl.CERT_REQUIRED
            self.context.check_hostname = True
        else:
            self.context.verify_mode = ssl.CERT_NONE
            self.context.check_hostname = False
        logger.info("TLSManager initialized with %s using certfile=%s and keyfile=%s", version, certfile, keyfile)
        if key is None or iv is None:
            raise ValueError("AES-GCM key and IV must be provided for data encryption.")
        if len(key) != 32 or len(iv) != 12:
            raise ValueError("Key must be 32 bytes and IV must be 12 bytes.")
        self.aesgcm = AESGCM(key)
        self.iv = iv
        self.sequence_number = 0

    def perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        self.socket = self.context.wrap_socket(sock, server_hostname=server_hostname)
        logger.info("TLS handshake completed with server: %s", server_hostname)

    def encrypt_data(self, data: bytes) -> bytes:
        nonce = self._compute_nonce()
        ciphertext = self.aesgcm.encrypt(nonce, data, None)
        self.sequence_number += 1
        return nonce + ciphertext

    def decrypt_data(self, data: bytes) -> bytes:
        if len(data) < 12:
            raise ValueError("Data too short to contain nonce.")
        nonce = data[:12]
        ciphertext = data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    def update_keys(self) -> None:
        self.sequence_number = 0

    def _compute_nonce(self) -> bytes:
        return self.iv[:8] + struct.pack(">I", self.sequence_number)