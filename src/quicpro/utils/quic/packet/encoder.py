"""
Encoder module for QUIC packets.
Encodes a stream frame into a QUIC packet.
"""

import hashlib


def encode_quic_packet(stream_frame: bytes) -> bytes:
    """
    Encode a QUIC packet:
      - Header: b'QUIC'
      - 4-byte big-endian length of stream_frame.
      - 8-byte truncated SHA256 checksum.
      - Payload: stream_frame.
    """
    header_marker = b'QUIC'
    frame_length = len(stream_frame)
    length_bytes = frame_length.to_bytes(4, byteorder='big')
    checksum = hashlib.sha256(stream_frame).digest()[:8]
    return header_marker + length_bytes + checksum + stream_frame
