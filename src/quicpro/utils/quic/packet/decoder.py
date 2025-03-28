"""
decoder.py - Decoder for QUIC packets.

This module provides a function to decode a QUIC packet and extract the contained
HTTP/3 stream frame. It supports two formats:
  1. Modern format:
     - Header marker: b'QUIC' (4 bytes)
     - Payload Length: 4-byte big-endian integer representing the stream_frame length.
     - Checksum: 8-byte truncated SHA256 digest of the stream frame.
     - Payload: The stream frame.
  2. Legacy/simulation format:
     - Header prefix: b'QUICFRAME:' followed by additional fields.
     - Expected format: b"QUICFRAME:<frame_id>:<seq_num>:<total_packets>:<payload>".
       The payload is extracted by splitting on b":" and using the fifth part.
If the packet does not match either format, the full packet is returned.
"""

import hashlib

def decode_quic_packet(packet: bytes) -> bytes:
    """
    Decode a QUIC packet and extract the stream frame.

    Args:
        packet (bytes): The raw QUIC packet.

    Returns:
        bytes: The extracted stream frame.

    Raises:
        ValueError: If the packet format is invalid or checksum verification fails.
    """
    if packet.startswith(b"QUICFRAME:"):
        # Legacy/simulation format handling
        parts = packet.split(b":", 4)
        if len(parts) != 5:
            raise ValueError("Invalid QUICFRAME packet format; expected 5 parts.")
        # parts: [b"QUICFRAME", frame_id, seq_num, total_packets, payload]
        return parts[4].strip()
    if packet.startswith(b'QUIC'):
        if len(packet) < 16:
            raise ValueError("Packet too short to be a valid QUIC packet.")
        length_bytes = packet[4:8]
        checksum = packet[8:16]
        stream_frame = packet[16:]
        expected_length = int.from_bytes(length_bytes, byteorder='big')
        if expected_length != len(stream_frame):
            raise ValueError("Stream frame length does not match the length field.")
        expected_checksum = hashlib.sha256(stream_frame).digest()[:8]
        if expected_checksum != checksum:
            raise ValueError("Checksum verification failed.")
        return stream_frame
    # Fallback: return entire packet if no known header is detected.
    return packet
