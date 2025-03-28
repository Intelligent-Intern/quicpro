"""
TLS 1.3 Context Implementation (Professional Version)
This implementation of TLS13Context extends the TLSContext abstract class.
It sets up an SSL context enforcing TLS 1.3, wraps a socket to perform the handshake,
and simulates encryption/decryption and key updates. In a production environment,
a dedicated TLS library with direct access to encryption keys and cipher APIs would be used.
"""

import ssl
import socket
import logging
from typing import Optional, Dict
from .tls_context import TLSContext
from .base import generate_random_bytes, log_tls_debug

logger = logging.getLogger(__name__)

class TLS13Context(TLSContext):
    def __init__(self, certfile: str, keyfile: str, cafile: Optional[str] = None) -> None:
        """
        Initialize TLS13Context with certificate and key.
        
        Args:
            certfile (str): Path to the certificate file.
            keyfile (str): Path to the private key file.
            cafile (Optional[str]): Path to the CA certificate bundle (if required).
        """
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # Enforce TLS 1.3 only.
        self.context.minimum_version = ssl.TLSVersion.TLSv1_3
        self.context.maximum_version = ssl.TLSVersion.TLSv1_3
        try:
            self.context.load_cert_chain(certfile, keyfile)
        except Exception as e:
            logger.exception("Failed to load certificate or key.")
            raise e

        if cafile:
            try:
                self.context.load_verify_locations(cafile)
                self.context.verify_mode = ssl.CERT_REQUIRED
            except Exception as e:
                logger.exception("Failed to load CA file.")
                raise e
        else:
            self.context.check_hostname = False
            self.context.verify_mode = ssl.CERT_NONE

        self._negotiated_keys: Optional[Dict[str, bytes]] = None
        self.handshake_completed: bool = False
        self.ssl_sock: Optional[ssl.SSLSocket] = None

    def perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        """
        Perform the full TLS 1.3 handshake over the provided socket.
        Wraps the socket with SNI enabled and calls do_handshake().
        
        Args:
            sock (socket.socket): A connected socket.
            server_hostname (str): The hostname to be used for SNI.
        
        Raises:
            ssl.SSLError: If the handshake fails.
            RuntimeError: If an unexpected error occurs.
        """
        log_tls_debug("Starting TLS 1.3 handshake")
        try:
            # Wrap the socket for TLS. The wrapped socket will perform the handshake automatically when do_handshake() is called.
            self.ssl_sock = self.context.wrap_socket(sock, server_hostname=server_hostname, do_handshake_on_connect=False)
            self.ssl_sock.do_handshake()
            self.handshake_completed = True
            # In absence of direct key extraction, simulate key derivation.
            self._negotiated_keys = {
                'read_key': generate_random_bytes(32),
                'write_key': generate_random_bytes(32)
            }
            log_tls_debug("TLS 1.3 handshake completed successfully")
        except ssl.SSLError as e:
            logger.exception("TLS 1.3 handshake failed")
            raise e
        except Exception as e:
            logger.exception("Unexpected error during TLS 1.3 handshake")
            raise RuntimeError("Unexpected error during handshake") from e

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext using negotiated TLS 1.3 keys.
        Since ssl.SSLContext does not provide direct encryption APIs, this method simulates encryption.
        
        Args:
            plaintext (bytes): Data to encrypt.
        
        Returns:
            bytes: Simulated ciphertext.
        
        Raises:
            RuntimeError: If handshake has not been performed.
        """
        if not self.handshake_completed or self._negotiated_keys is None:
            raise RuntimeError("TLS 1.3 handshake has not been completed. Cannot encrypt data.")
        # Simulate encryption by prefixing with a marker.
        simulated_prefix = b"TLS13_ENC:"
        ciphertext = simulated_prefix + plaintext
        log_tls_debug(f"Simulated encryption completed for {len(plaintext)} bytes")
        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext using negotiated TLS 1.3 keys.
        This method simulates decryption by removing the simulated encryption marker.
        
        Args:
            ciphertext (bytes): Data to decrypt.
        
        Returns:
            bytes: Decrypted plaintext.
        
        Raises:
            RuntimeError: If handshake has not been completed.
            ValueError: If ciphertext does not have the expected format.
        """
        if not self.handshake_completed or self._negotiated_keys is None:
            raise RuntimeError("TLS 1.3 handshake has not been completed. Cannot decrypt data.")
        simulated_prefix = b"TLS13_ENC:"
        if not ciphertext.startswith(simulated_prefix):
            raise ValueError("Ciphertext format invalid: missing expected TLS13_ENC header.")
        plaintext = ciphertext[len(simulated_prefix):]
        log_tls_debug(f"Simulated decryption completed for {len(plaintext)} bytes")
        return plaintext

    def update_keys(self) -> None:
        """
        Update (rotate) the negotiated TLS keys per TLS 1.3 key update procedure.
        This method simulates key update by generating new random keys.
        
        Raises:
            RuntimeError: If handshake has not been completed.
        """
        if not self.handshake_completed:
            raise RuntimeError("TLS 1.3 handshake has not been completed. Cannot update keys.")
        self._negotiated_keys = {
            'read_key': generate_random_bytes(32),
            'write_key': generate_random_bytes(32)
        }
        log_tls_debug("Simulated TLS 1.3 key update performed")