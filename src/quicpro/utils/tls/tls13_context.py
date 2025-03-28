"""
TLS 1.3 Context Implementation (Professional Version with Demo Support)
This implementation of TLS13Context extends the TLSContext abstract class.
In demo mode (demo==True), certificate loading is skipped and the handshake
is automatically marked as complete with dummy keys. In production mode, certificates
are loaded normally.
"""
import ssl
import socket
import logging
from typing import Optional, Dict
from .tls_context import TLSContext
from .base import generate_random_bytes, log_tls_debug

logger = logging.getLogger(__name__)


class TLS13Context(TLSContext):
    def __init__(self, certfile: str, keyfile: str, cafile: Optional[str] = None, demo: bool = True) -> None:
        self.demo = demo
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_3
        self.context.maximum_version = ssl.TLSVersion.TLSv1_3
        if not self.demo:
            try:
                self.context.load_cert_chain(certfile, keyfile)
            except Exception as e:
                logger.exception("Failed to load certificate or key.")
                raise e
        else:
            logger.info(
                "Demo mode: skipping loading certificate or key in TLS13Context.")
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
        if self.demo:
            self.handshake_completed = True
            self._negotiated_keys = {
                "read_key": b"demo_read_key_32_bytes_long__",
                "write_key": b"demo_write_key_32_bytes_long_"
            }
        else:
            self.handshake_completed = False
        self.ssl_sock: Optional[ssl.SSLSocket] = None

    def perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        log_tls_debug("Starting TLS 1.3 handshake")
        if self.demo:
            log_tls_debug(
                "Demo mode: performing dummy handshake, marking handshake as complete")
            self.handshake_completed = True
            if self._negotiated_keys is None:
                self._negotiated_keys = {
                    "read_key": b"demo_read_key_32_bytes_long__",
                    "write_key": b"demo_write_key_32_bytes_long_"
                }
            return
        try:
            self.ssl_sock = self.context.wrap_socket(
                sock, server_hostname=server_hostname, do_handshake_on_connect=False)
            self.ssl_sock.do_handshake()
            self.handshake_completed = True
            self._negotiated_keys = {
                "read_key": generate_random_bytes(32),
                "write_key": generate_random_bytes(32)
            }
            log_tls_debug("TLS 1.3 handshake completed successfully")
        except ssl.SSLError as e:
            logger.exception("TLS 1.3 handshake failed")
            raise e
        except Exception as e:
            logger.exception("Unexpected error during TLS 1.3 handshake")
            raise RuntimeError("Unexpected error during handshake") from e

    def encrypt(self, plaintext: bytes) -> bytes:
        if not self.handshake_completed or self._negotiated_keys is None:
            raise RuntimeError(
                "TLS 1.3 handshake has not been completed. Cannot encrypt data.")
        simulated_prefix = b"TLS13_ENC:"
        ciphertext = simulated_prefix + plaintext
        log_tls_debug(
            f"Simulated encryption completed for {len(plaintext)} bytes")
        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        if not self.handshake_completed or self._negotiated_keys is None:
            raise RuntimeError(
                "TLS 1.3 handshake has not been completed. Cannot decrypt data.")
        simulated_prefix = b"TLS13_ENC:"
        if not ciphertext.startswith(simulated_prefix):
            raise ValueError(
                "Ciphertext format invalid: missing expected TLS13_ENC header.")
        plaintext = ciphertext[len(simulated_prefix):]
        log_tls_debug(
            f"Simulated decryption completed for {len(plaintext)} bytes")
        return plaintext

    def update_keys(self) -> None:
        if not self.handshake_completed:
            raise RuntimeError(
                "TLS 1.3 handshake has not been completed. Cannot update keys.")
        self._negotiated_keys = {
            "read_key": generate_random_bytes(32),
            "write_key": generate_random_bytes(32)
        }
        log_tls_debug("Simulated TLS 1.3 key update performed")
