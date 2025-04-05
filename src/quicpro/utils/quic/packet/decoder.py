#!/usr/bin/env python
"""
Production-Perfect QUIC Packet Decoder

This module decodes a QUIC packet and extracts the encapsulated stream frame payload.
The production packet format is defined as follows:
  - 4 bytes: Header marker ("QUIC")
  - 4 bytes: Payload length (big-endian)
  - 8 bytes: Checksum (truncated SHA256 digest of the payload)
  - Payload: The stream frame payload
"""

import hashlib
import struct

HEADER_MARKER = b'QUIC'

def decode_quic_packet(packet: bytes) -> bytes:
    if not packet.startswith(HEADER_MARKER):
        raise ValueError("Packet does not start with the required header marker.")
    if len(packet) < 16:
        raise ValueError("Packet too short to contain a valid header.")
    payload_length = int.from_bytes(packet[4:8], byteorder='big')
    checksum = packet[8:16]
    if len(packet) < 16 + payload_length:
        raise ValueError("Packet payload length mismatch.")
    payload = packet[16:16+payload_length]
    computed_checksum = hashlib.sha256(payload).digest()[:8]
    if computed_checksum != checksum:
        raise ValueError("Checksum verification failed.")
    return payload
