#!/usr/bin/env python
"""
Production-Perfect QUIC Packet Encoder

This module encodes a stream frame payload into a QUIC packet.
The packet format is as follows:
  - 4 bytes: Header marker ("QUIC")
  - 4 bytes: Payload length (big-endian)
  - 8 bytes: Checksum (truncated SHA256 digest of the payload)
  - Payload bytes
"""

import hashlib

HEADER_MARKER = b'QUIC'

def encode_quic_packet(payload: bytes) -> bytes:
    """
    Encode a stream frame payload into a QUIC packet.

    Args:
        payload (bytes): The complete payload to be encoded.

    Returns:
        bytes: The encoded QUIC packet.

    Raises:
        ValueError: If the payload is empty.
    """
    if not payload:
        raise ValueError("Payload cannot be empty.")
    payload_length = len(payload)
    length_bytes = payload_length.to_bytes(4, byteorder='big')
    checksum = hashlib.sha256(payload).digest()[:8]
    return HEADER_MARKER + length_bytes + checksum + payload
