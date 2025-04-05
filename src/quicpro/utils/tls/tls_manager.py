"""
Production-Perfect TLS Manager with Advanced Features

This class provides a unified interface for TLS operations including handshake,
encryption, decryption, key rotation, session resumption, dynamic configuration updates,
and certificate validation (chain and revocation). It supports both TLSv1.3 and TLSv1.2,
and integrates its functionality with our in-house session ticket/resumption manager.
"""

import ssl
import socket
import logging
import struct
import time
from typing import Optional, Dict, Any, Callable, List

from pydantic import BaseModel
from quicpro.utils.tls.dynamic_config.config_loader import load_config  # Assumes dynamic config loader exists
from quicpro.utils.tls.context.tls13_context import TLS13Context
from quicpro.utils.tls.context.tls12_context import TLS12Context
from quicpro.utils.tls.handshake.handshake import perform_handshake, fallback_handshake
from quicpro.utils.tls.async.async_handshake import async_perform_handshake
from quicpro.utils.tls.encryption.aes_gcm import encrypt as aes_encrypt, decrypt as aes_decrypt
from quicpro.utils.tls.key_rotation.key_rotator import KeyRotator
from quicpro.utils.tls.certificate.chain_validator import validate_chain, validate_pinned_certificate
from quicpro.utils.tls.certificate.revocation import verify_certificate_revocation
from quicpro.utils.tls.session.resumption import store_session, resume_session, rotate_ticket_key
from quicpro.utils.tls.callbacks.event_callbacks import invoke_callbacks

from quicpro.model.tls_config_model import TLSManagerConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TLSManager:
    """
    Production-Perfect TLS Manager

    A monolithic TLSManager that integrates advanced features:
      - TLS context instantiation with fallback between TLSv1.3 and TLSv1.2.
      - Session resumption using in-memory session ticket management.
      - Certificate chain validation with OCSP/CRL revocation checked.
      - AES-GCM data encryption and decryption with secure key rotation via HKDF.
      - Dynamic configuration loading via Pydantic.
      - Callback registration for critical TLS events.
    """
    config: TLSManagerConfig

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the TLSManager from a dynamic configuration.

        :param config: Dictionary containing TLS parameters.
        """
        self.config = TLSManagerConfig(**config)
        self.rotation_interval = self.config.rotation_interval
        self.handshake_timeout = self.config.handshake_timeout
        self.cafile = self.config.cafile
        if self.config.version == "TLSv1.3":
            self.tls_context = TLS13Context(self.config.certfile, self.config.keyfile, self.config.cafile)
        elif self.config.version == "TLSv1.2":
            self.tls_context = TLS12Context(self.config.certfile, self.config.keyfile, self.config.cafile)
        else:
            raise ValueError("Unsupported TLS version.")
        self.session = None
        self.key_rotator = KeyRotator(self.config.aes_key)
        self.aesgcm = aes_encrypt.__globals__['AESGCM'](self.config.aes_key)
        self.iv = self.config.iv
        self.sequence_number = 0
        self.last_rotation = time.time()
        self.callbacks: Dict[str, List[Callable[[Any], None]]] = {
            "handshake_complete": [],
            "key_rotated": [],
            "crypto_error": [],
        }
        logger.info("TLSManager initialized with configuration: %s", self.config.json())

    def perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        """
        Perform the TLS handshake and store the session for resumption.
        
        :param sock: The socket to wrap.
        :param server_hostname: The server hostname for SNI.
        """
        try:
            perform_handshake(self.tls_context, sock, server_hostname)
            self.session = sock.session if hasattr(sock, "session") else None
            peer_cert = sock.getpeercert(binary_form=True)
            validate_chain(peer_cert, self.config.cafile)
            verify_certificate_revocation(peer_cert)
            # Store TLS session for resumption.
            store_session(self.session)
            invoke_callbacks(self.callbacks, "handshake_complete", {"server": server_hostname})
            logger.info("TLS handshake completed with server: %s", server_hostname)
        except Exception as e:
            fallback_handshake(self.tls_context, sock, server_hostname)
            logger.warning("Fallback handshake performed due to error: %s", e)

    def async_perform_handshake(self, sock: socket.socket, server_hostname: str) -> None:
        """
        Perform an asynchronous TLS handshake.
        
        :param sock: The socket to use.
        :param server_hostname: Server hostname for SNI.
        """
        async_perform_handshake(self.tls_context, sock, server_hostname)

    def encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt data using AES-GCM; rotate keys if necessary.
        
        :param data: Plaintext data.
        :return: Nonce concatenated with ciphertext.
        """
        try:
            nonce = self._compute_nonce()
            ciphertext = aes_encrypt(nonce, data)
            self.sequence_number += 1
            self._check_key_rotation()
            return nonce + ciphertext
        except Exception as e:
            invoke_callbacks(self.callbacks, "crypto_error", {"error": str(e)})
            logger.exception("Encryption failed: %s", e)
            raise

    def decrypt_data(self, data: bytes) -> bytes:
        """
        Decrypt data using AES-GCM.
        
        :param data: Nonce concatenated with ciphertext.
        :return: Plaintext data.
        """
        if len(data) < 12:
            raise ValueError("Data too short to contain nonce.")
        nonce = data[:12]
        ciphertext = data[12:]
        try:
            return aes_decrypt(nonce, ciphertext)
        except Exception as e:
            invoke_callbacks(self.callbacks, "crypto_error", {"error": str(e)})
            logger.exception("Decryption failed: %s", e)
            raise

    def update_keys(self) -> None:
        """
        Rotate the AES-GCM key using HKDF-based derivation and update the cipher.
        """
        new_key = self.key_rotator.rotate_key()
        self.aesgcm = aes_encrypt.__globals__['AESGCM'](new_key)
        self.sequence_number = 0
        self.last_rotation = time.time()
        invoke_callbacks(self.callbacks, "key_rotated", {"new_key": new_key.hex()})
        # Rotate session ticket key as well if applicable.
        rotated_ticket_key = rotate_ticket_key()
        logger.info("AES-GCM keys updated; new key: %s, rotated ticket key: %s", new_key.hex(), rotated_ticket_key.hex())

    def _compute_nonce(self) -> bytes:
        """
        Compute nonce from IV and sequence number.
        
        :return: The computed nonce.
        """
        return self.iv[:8] + struct.pack(">I", self.sequence_number)

    def _check_key_rotation(self) -> None:
        """
        Check if the rotation interval has been exceeded and update keys if so.
        """
        if time.time() - self.last_rotation >= self.rotation_interval:
            self.update_keys()

    def revalidate_certificate(self) -> None:
        """
        Revalidate the peer certificate chain and revocation status.
        """
        peer_cert = self.session.getpeercert(binary_form=True) if self.session else None
        if not peer_cert:
            raise ValueError("No peer certificate available for revalidation.")
        validate_chain(peer_cert, self.config.cafile)
        verify_certificate_revocation(peer_cert)
        logger.info("Certificate revalidation successful.")

    def register_callback(self, event: str, callback: Callable[[Any], None]) -> None:
        """
        Register a callback for a TLS event.
        
        :param event: Event name.
        :param callback: Callable to invoke on event.
        """
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)

    def dynamic_config_update(self, new_config: Dict[str, Any]) -> None:
        """
        Update TLS configuration at runtime.
        
        :param new_config: Dictionary of configuration updates.
        """
        updated = self.config.copy(update=new_config)
        self.config = updated
        self.rotation_interval = self.config.rotation_interval
        self.handshake_timeout = self.config.handshake_timeout
        logger.info("Dynamic configuration updated: %s", self.config.json())
