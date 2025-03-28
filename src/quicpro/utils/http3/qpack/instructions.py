"""
Dynamic Table Size Update Instruction Encoding for QPACK

This module provides a function to encode dynamic table size update instructions
as defined by QPACK.
"""

from .varint import encode_integer


def encode_dynamic_table_size_update(new_max_size: int) -> bytes:
    """
    Encode a dynamic table size update instruction.

    The instruction uses a 3-bit prefix (e.g., '001' in the high-order bits) followed
    by the new maximum size encoded as a variable-length integer.

    Args:
        new_max_size (int): The new maximum dynamic table size.

    Returns:
        bytes: The encoded dynamic table size update instruction.
    """
    prefix = 0b001 << 5
    return bytes([prefix]) + encode_integer(new_max_size, 5)
