"""
Variable-Length Integer Encoding for QPACK

This module provides the function to encode integers using the QPACK/HPACK
variable-length integer encoding scheme.
"""

def encode_integer(value: int, prefix_bits: int) -> bytes:
    """
    Encode an integer using QPACK's variable-length integer encoding.

    Args:
        value (int): The integer to encode.
        prefix_bits (int): The number of bits available in the first byte.

    Returns:
        bytes: The encoded integer.

    Raises:
        ValueError: If the value is negative.
    """
    if value < 0:
        raise ValueError("Cannot encode a negative integer.")
    prefix_max = (1 << prefix_bits) - 1
    if value < prefix_max:
        return bytes([value])
    result = bytearray([prefix_max])
    value -= prefix_max
    while value >= 128:
        result.append((value % 128) + 128)
        value //= 128
    result.append(value)
    return bytes(result)
