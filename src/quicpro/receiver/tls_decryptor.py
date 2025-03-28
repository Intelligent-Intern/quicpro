"""
TLS Decryptor Module

This module decrypts incoming AES-GCM encrypted UDP datagrams and passes the
decrypted QUIC packet to a QUICReceiver. It supports two modes:
  - Demo mode: Uses AES-GCM decryption with a static IV (from TLSConfig) and a demo
    sequence number scheme.
  - Real mode: Uses a provided DTLS/TLS context to decrypt the packet, allowing for
    full TLS 1.1/1.2/1.3 support with user-defined certificates.

A parameter 'demo' (True/False) selects between these modes.
"""

import logging
from typing import Any, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.model.tls_config import TLSConfig
from quicpro.exceptions.decryption_error import DecryptionError

logger = logging.getLogger(__name__)


class TLSDecryptor:
    """
    Decrypts AES-GCM encrypted UDP datagrams and routes the decrypted QUIC packet
    to a QUICReceiver.

    In demo mode, decryption is performed using AES-GCM with a nonce derived from a
    static IV and a demo sequence number. In real mode, a DTLS/TLS context is used
    for decryption.
    """
    def __init__(
        self,
        quic_receiver: Any,
        config: TLSConfig,
        demo: bool = True,
        dtls_context: Optional[Any] = None
    ) -> None:
        """
        Initialize the TLSDecryptor.

        Args:
            quic_receiver (Any): An instance with a receive(packet: bytes) method.
            config (TLSConfig): TLS configuration containing a 32-byte key and 12-byte IV.
            demo (bool, optional): If True, use demo decryption; if False, use real TLS decryption.
                                     Defaults to True.
            dtls_context (Optional[Any], optional): A DTLS/TLS context for real decryption.
                                                     Required if demo is False.
        """
        self.quic_receiver = quic_receiver
        self.config = config
        self.demo = demo
        self.dtls_context = dtls_context
        if self.demo:
            self.aesgcm = AESGCM(self.config.key)
        else:
            if self.dtls_context is None:
                raise DecryptionError("Real TLS decryption mode requires a DTLS/TLS context.")
            logger.info("Real TLS decryption mode activated.")

    def _compute_nonce(self, seq_number: int) -> bytes:
        """
        Compute the nonce for decryption by XOR-ing the static IV with the sequence number.

        Args:
            seq_number (int): The sequence number extracted from the packet.

        Returns:
            bytes: The computed nonce.
        """
        seq_bytes = seq_number.to_bytes(12, byteorder="big")
        return bytes(iv_byte ^ seq_byte for iv_byte, seq_byte in zip(self.config.iv, seq_bytes))

    def decrypt(self, encrypted_packet: bytes) -> None:
        """
        Decrypt an encrypted UDP datagram and pass the decrypted QUIC packet to the QUICReceiver.

        In demo mode, the packet is expected to have an 8-byte sequence number prefix,
        followed by the AES-GCM ciphertext. In real mode, the DTLS/TLS context handles decryption.

        Args:
            encrypted_packet (bytes): The encrypted UDP datagram.

        Raises:
            DecryptionError: If decryption fails.
        """
        if self.demo:
            try:
                if len(encrypted_packet) < 9:
                    raise ValueError("Encrypted packet is too short.")
                seq_number = int.from_bytes(encrypted_packet[:8], byteorder="big")
                ciphertext = encrypted_packet[8:]
                nonce = self._compute_nonce(seq_number)
                quic_packet = self.aesgcm.decrypt(nonce, ciphertext, None)
                logger.info("Decrypted packet with sequence number %d", seq_number)
                self.quic_receiver.receive(quic_packet)
            except Exception as e:
                logger.exception("TLSDecryptor demo decryption failed: %s", e)
                raise DecryptionError(f"Demo decryption failed: {e}") from e
        else:
            try:
                # Real TLS decryption branch using the provided dtls_context.
                quic_packet = self.dtls_context.decrypt(encrypted_packet)
                logger.info("Decrypted packet using real TLS context.")
                self.quic_receiver.receive(quic_packet)
            except Exception as e:
                logger.exception("TLSDecryptor real decryption failed: %s", e)
                raise DecryptionError(f"Real decryption failed: {e}") from e
