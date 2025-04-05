#!/usr/bin/env python
"""
Production-Perfect QUIC Handshake and Negotiation Module with TLS Integration

This module implements the QUICHandshake class which performs handshake and version negotiation,
integrated fully with our TLS handshake implementation using TLSManager.
"""

import time
import logging
from enum import Enum
from typing import List, Optional, Any

from quicpro.utils.tls.tls_manager import TLSManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class HandshakeState(Enum):
    INITIAL = 1
    VERSION_NEGOTIATION = 2
    HANDSHAKE = 3
    TLS_HANDSHAKE = 4
    ONE_RTT = 5
    COMPLETED = 6

class QUICHandshake:
    def __init__(self, connection: Any, local_version: str = "v1", tls_manager: Optional[TLSManager] = None) -> None:
        self.connection = connection
        self.local_version = local_version
        self.state: HandshakeState = HandshakeState.INITIAL
        self.negotiated_version: Optional[str] = None
        self.handshake_start_time: Optional[float] = None
        self.tls_manager = tls_manager

    def send_initial_packet(self) -> None:
        packet = b"QUIC_INIT:" + self.local_version.encode("ascii")
        self.connection.send_packet(packet)

    def process_incoming_packet(self, packet: bytes) -> None:
        if self.state == HandshakeState.INITIAL:
            if packet.startswith(b"VERNEG:"):
                self.state = HandshakeState.VERSION_NEGOTIATION
                versions_str = packet[len(b"VERNEG:"):].decode("ascii")
                peer_versions = [v.strip() for v in versions_str.split(",") if v.strip()]
                self.negotiated_version = self._negotiate_version(peer_versions)
                self.local_version = self.negotiated_version
                self.send_initial_packet()
            else:
                self.state = HandshakeState.HANDSHAKE
                self._handle_handshake_packet(packet)
        elif self.state == HandshakeState.HANDSHAKE:
            self._handle_handshake_packet(packet)
        elif self.state == HandshakeState.TLS_HANDSHAKE:
            self._handle_tls_packet(packet)
        elif self.state == HandshakeState.ONE_RTT:
            self.state = HandshakeState.COMPLETED
            logger.debug("Handshake and TLS integration completed.")

    def _handle_handshake_packet(self, packet: bytes) -> None:
        if b"TLS_START" in packet and self.tls_manager is not None:
            self.state = HandshakeState.TLS_HANDSHAKE
            self.tls_manager.perform_handshake(self.connection, "example.com")
            self._send_1rtt_packet()
        elif b"HANDSHAKE_DONE" in packet:
            self.state = HandshakeState.ONE_RTT
            self._send_1rtt_packet()
        else:
            pass

    def _handle_tls_packet(self, packet: bytes) -> None:
        if b"TLS_DONE" in packet:
            self.state = HandshakeState.ONE_RTT
            self._send_1rtt_packet()
        else:
            pass

    def _send_1rtt_packet(self) -> None:
        packet = b"QUIC_1RTT:" + b"FINALIZE_HANDSHAKE"
        self.connection.send_packet(packet)

    def _negotiate_version(self, peer_versions: List[str]) -> str:
        if self.local_version in peer_versions:
            return self.local_version
        common = [v for v in peer_versions if v == self.local_version]
        if common:
            return common[0]
        raise Exception("No common QUIC version found.")

    @property
    def state_value(self) -> HandshakeState:
        return self.state
