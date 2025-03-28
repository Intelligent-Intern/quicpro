"""
base.py - Low-level utilities for QUIC header operations.

This module provides functions for variable-length integer encoding and decoding.
"""


def encode_varint(value: int) -> bytes:
    """Encode an integer using QUIC's variable-length integer encoding rules."""
    if value < 0x40:
        return value.to_bytes(1, 'big')
    if value < 0x4000:
        return (value | 0x4000).to_bytes(2, 'big')
    if value < 0x40000000:
        return (value | 0x80000000).to_bytes(4, 'big')
    if value < 0x4000000000000000:
        return (value | 0xC000000000000000).to_bytes(8, 'big')
    raise ValueError("Integer value too large for QUIC varint encoding.")


def decode_varint(data: bytes) -> (int, int):
    """Decode a varint from the given data.

    Returns:
        tuple: (decoded integer, number of bytes consumed)
    """
    if not data:
        raise ValueError("No data provided for decoding varint.")
    first_byte = data[0]
    prefix = first_byte >> 6
    if prefix == 0:
        return first_byte, 1
    if prefix == 1:
        if len(data) < 2:
            raise ValueError("Insufficient data for 2-byte varint.")
        value = int.from_bytes(data[:2], "big") & 0x3FFF
        return value, 2
    if prefix == 2:
        if len(data) < 4:
            raise ValueError("Insufficient data for 4-byte varint.")
        value = int.from_bytes(data[:4], "big") & 0x3FFFFFFF
        return value, 4
    if prefix == 3:
        if len(data) < 8:
            raise ValueError("Insufficient data for 8-byte varint.")
        value = int.from_bytes(data[:8], "big") & 0x3FFFFFFFFFFFFFFF
        return value, 8
    raise ValueError("Invalid varint prefix.")
