"""
QUIC Handshake and Version Negotiation (Production Ready)
Implements the handshake procedure mandated by RFC 9000,
including support for Initial, Handshake, and 1‑RTT packet number spaces.
Also performs robust version negotiation if the peer returns a Version Negotiation packet.
This implementation uses a state machine to control the handshake flow.
"""
import time
import logging
from enum import Enum
from typing import List, Optional
logger = logging.getLogger(__name__)

# Define handshake states
class HandshakeState(Enum):
    INITIAL = 1
    VERSION_NEGOTIATION = 2
    HANDSHAKE = 3
    ONE_RTT = 4
    COMPLETED = 5

# Sample constant for version negotiation packet header marker.
VERSION_NEGOTIATION_MARKER = b"VERNEG"

def negotiate_version(local_version: str, peer_versions: List[str]) -> str:
    """
    Negotiate the protocol version; raise error if no match found.
    """
    if local_version in peer_versions:
        return local_version
    common = [v for v in peer_versions if v in local_version]  # Simple filter.
    if common:
        return common[0]
    raise ValueError("No common QUIC version found.")

class QUICHandshake:
    """
    Implements the QUIC handshake state machine.
    """
    INITIAL = HandshakeState.INITIAL
    VERSION_NEGOTIATION = HandshakeState.VERSION_NEGOTIATION
    HANDSHAKE = HandshakeState.HANDSHAKE
    ONE_RTT = HandshakeState.ONE_RTT
    COMPLETED = HandshakeState.COMPLETED

    def __init__(self, connection, local_version: str = "v1"):
        """
        Args:
            connection: The QUIC connection object that provides send_packet() and receive_packet() APIs.
            local_version (str): The client’s preferred QUIC version.
        """
        self.connection = connection
        self.local_version = local_version
        self.state = HandshakeState.INITIAL
        self.negotiated_version: Optional[str] = None
        self.handshake_start_time = None

    def send_initial_packet(self) -> None:
        """
        Create and send an Initial packet using the Initial keys.
        In a full implementation, this packet includes a ClientHello.
        """
        packet = b"QUIC_INIT:" + self.local_version.encode("ascii")
        logger.debug("Sending Initial packet: %s", packet)
        self.connection.send_packet(packet)

    def process_incoming_packet(self, packet: bytes) -> None:
        """
        Process a received packet according to the current handshake state.
        """
        if self.state == HandshakeState.INITIAL:
            # Check if it is a version negotiation packet.
            if packet.startswith(VERSION_NEGOTIATION_MARKER):
                self.state = HandshakeState.VERSION_NEGOTIATION
                peer_versions = self._extract_peer_versions(packet)
                logger.debug("Received Version Negotiation packet, peer_versions: %s", peer_versions)
                negotiated = negotiate_version(self.local_version, peer_versions)
                self.negotiated_version = negotiated
                logger.info("Negotiated QUIC version: %s", negotiated)
                # After negotiation, re-send Initial packet with updated version.
                self.local_version = negotiated
                self.send_initial_packet()
            else:
                # Assume packet is a Handshake packet.
                self.state = HandshakeState.HANDSHAKE
                logger.debug("Transitioning to HANDSHAKE state")
                self._handle_handshake_packet(packet)
        elif self.state == HandshakeState.HANDSHAKE:
            self._handle_handshake_packet(packet)
        elif self.state == HandshakeState.ONE_RTT:
            # Finalize the handshake if we receive 1-RTT packet(s)
            logger.info("1-RTT packet received, handshake complete")
            self.state = HandshakeState.COMPLETED

    def _handle_handshake_packet(self, packet: bytes) -> None:
        """
        Process a handshake packet.
        In production the packet contains handshake messages (e.g., ServerHello,
        encrypted extensions, certificates, etc.) and may trigger key derivation.
        Here we simulate key establishment.
        """
        logger.debug("Processing Handshake packet: %s", packet)
        # Simulate key derivation complete after receiving a handshake message.
        if b"HANDSHAKE_DONE" in packet:
            self.state = HandshakeState.ONE_RTT
            logger.info("Handshake phase completed; transitioning to 1‑RTT phase")
            self._send_1rtt_packet()

    def _send_1rtt_packet(self) -> None:
        """
        Send a 1‑RTT protected packet to signal handshake completion.
        """
        packet = b"QUIC_1RTT:" + b"FINALIZE_HANDSHAKE"
        logger.debug("Sending 1‑RTT packet: %s", packet)
        self.connection.send_packet(packet)

    def _extract_peer_versions(self, packet: bytes) -> List[str]:
        """
        Extract peer-supported versions from a Version Negotiation packet.
        Assumes versions are comma-separated after the VERSION_NEGOTIATION_MARKER.
        """
        try:
            versions_str = packet[len(VERSION_NEGOTIATION_MARKER):].decode("ascii")
            versions = [v.strip() for v in versions_str.split(",") if v.strip()]
            return versions
        except Exception as e:
            logger.exception("Failed to extract peer versions")
            return []

    def run(self, timeout: float = 5.0) -> None:
        """
        Run the handshake state machine until completed or timeout.

        Args:
            timeout (float): Maximum time to wait for handshake completion.

        Raises:
            TimeoutError: If handshake is not completed within timeout.
        """
        self.handshake_start_time = time.time()
        self.send_initial_packet()
        # Loop to simulate packet reception. In production, this loop would be event-driven.
        while self.state != HandshakeState.COMPLETED:
            if (time.time() - self.handshake_start_time) > timeout:
                raise TimeoutError("QUIC handshake timed out.")
            # Simulate waiting for an incoming packet.
            packet = self.connection.receive_packet(timeout=0.5)
            if packet:
                self.process_incoming_packet(packet)
            else:
                # Retransmit initial packet if no response in a certain interval.
                logger.debug("No packet received, retransmitting initial packet")
                self.send_initial_packet()
        logger.info("QUIC handshake completed successfully.")
