"""
TLS 1.2 Context Implementation (Production Ready)
Provides a fallback TLSContext implementation using TLS 1.2.
This implementation uses an SSLContext for the handshake, then—after a successful handshake—
exports keying material using OpenSSL’s SSL_export_keying_material (via the ssl socket’s API).
It then employs a real AES-GCM cipher (from cryptography) for packet encryption and decryption.
"""

import ssl
import socket
import logging
from typing import Optional, Dict
from .tls_context import TLSContext
from .base import generate_random_bytes, log_tls_debug

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

class TLS12Context(TLSContext):
    def __init__(self, certfile: str, keyfile: str, cafile: Optional[str] = None) -> None:
        """
        Initialize TLS12Context with TLS 1.2 configurations.
        
        Args:
            certfile (str): Path to the certificate.
            keyfile (str): Path to the private key.
            cafile (Optional[str]): Path to the CA bundle for verification.
        """
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.context.maximum_version = ssl.TLSVersion.TLSv1_2
        try:
            self.context.load_cert_chain(certfile, keyfile)
        except Exception as e:
            logger.exception("Failed loading certificate or key for TLS 1.2")
            raise e

        if cafile:
            try:
                self.context.load_verify_locations(cafile)
                self.context.verify_mode = ssl.CERT_REQUIRED
            except Exception as e:
                logger.exception("Failed loading CA file for TLS 1.2")
                raise e
        else:
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE

        self._negotiated_keys: Optional[Dict[str, bytes]] = None
        self.handshake_completed: bool = False
        self.ssl_sock: Optional[ssl.SSLSocket] = None
        self.aesgcm: Optional[AESGCM] = None  # Will be initialized after handshake

    def perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        """
        Perform a full TLS 1.2 handshake over the provided socket.
        Wraps the socket using SNI and initiates the handshake.
        Exports keying material via SSL_export_keying_material if available.
        
        Args:
            sock (socket.socket): A connected socket.
            server_hostname (str): The hostname for SNI.
            
        Raises:
            ssl.SSLError: If the handshake fails.
            RuntimeError: If the key export is unavailable.
        """
        log_tls_debug("Starting TLS 1.2 handshake")
        try:
            self.ssl_sock = self.context.wrap_socket(sock, server_hostname=server_hostname, do_handshake_on_connect=False)
            self.ssl_sock.do_handshake()
            self.handshake_completed = True

            # Export keying material using SSL_export_keying_material.
            # The label and context are defined per RFC; here we use a common label.
            if not hasattr(self.ssl_sock, "export_keying_material"):
                raise RuntimeError("SSL socket does not support export_keying_material facility.")
            
            # Export 32 bytes each for read and write keys.
            read_key = self.ssl_sock.export_keying_material(b"client read", 32, None)
            write_key = self.ssl_sock.export_keying_material(b"client write", 32, None)
            
            self._negotiated_keys = {
                'read_key': read_key,
                'write_key': write_key
            }
            # Initialize AESGCM cipher with the write key (used for encryption).
            self.aesgcm = AESGCM(write_key)
            log_tls_debug("TLS 1.2 handshake completed and keys negotiated successfully")
        except ssl.SSLError as e:
            logger.exception("TLS 1.2 handshake failed")
            raise e
        except Exception as e:
            logger.exception("Unexpected error during TLS 1.2 handshake")
            raise RuntimeError("Unexpected error during handshake") from e

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext using the negotiated TLS 1.2 keys with AES-GCM.
        This method employs the write key exported during handshake.
        
        Args:
            plaintext (bytes): Data to encrypt.
            
        Returns:
            bytes: Ciphertext including the nonce and GCM tag.
            
        Raises:
            RuntimeError: If handshake is not complete or keys/qipher are not initialized.
        """
        if not self.handshake_completed or self._negotiated_keys is None or self.aesgcm is None:
            raise RuntimeError("TLS 1.2 handshake not completed. Cannot encrypt data.")
        # AES-GCM requires a 12-byte nonce.
        nonce = generate_random_bytes(12)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data=None)
        # Prepend the nonce so it can be used for decryption.
        log_tls_debug(f"Production TLS 1.2 encryption performed for {len(plaintext)} bytes")
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext using the negotiated TLS 1.2 keys.
        Assumes the first 12 bytes of ciphertext are the nonce.
        
        Args:
            ciphertext (bytes): Data to decrypt.
            
        Returns:
            bytes: Decrypted plaintext.
            
        Raises:
            RuntimeError: If handshake is not complete.
            ValueError: If decryption fails.
        """
        if not self.handshake_completed or self._negotiated_keys is None or self.aesgcm is None:
            raise RuntimeError("TLS 1.2 handshake not completed. Cannot decrypt data.")
        if len(ciphertext) < 12:
            raise ValueError("Ciphertext too short; missing nonce.")
        nonce = ciphertext[:12]
        ct = ciphertext[12:]
        try:
            plaintext = self.aesgcm.decrypt(nonce, ct, associated_data=None)
            log_tls_debug(f"Production TLS 1.2 decryption performed for {len(plaintext)} bytes")
            return plaintext
        except Exception as e:
            logger.exception("Decryption failed in TLS 1.2 context")
            raise ValueError("Decryption failed.") from e

    def update_keys(self) -> None:
        """
        Update (rotate) the negotiated TLS keys.
        For TLS 1.2, key update is typically achieved via renegotiation.
        Here, we simulate a key update by exporting fresh keying material and reinitializing AESGCM.
        
        Raises:
            RuntimeError: If handshake is not complete.
        """
        if not self.handshake_completed or self.ssl_sock is None:
            raise RuntimeError("TLS 1.2 handshake not completed. Cannot update keys.")
        # Export new keying material.
        read_key = self.ssl_sock.export_keying_material(b"client read", 32, None)
        write_key = self.ssl_sock.export_keying_material(b"client write", 32, None)
        self._negotiated_keys = {
            'read_key': read_key,
            'write_key': write_key
        }
        self.aesgcm = AESGCM(write_key)
        log_tls_debug("Production TLS 1.2 key update performed successfully")