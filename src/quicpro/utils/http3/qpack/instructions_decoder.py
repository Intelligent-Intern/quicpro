"""
Dynamic Table Size Update Instruction Decoder for QPACK

This module provides a function to decode dynamic table size update instructions
from a QPACK header block, as defined in RFC 9204. Such an instruction uses a
3-bit prefix (e.g. '001') followed by a variable-length integer (with a 5-bit prefix)
representing the new maximum dynamic table size.
"""

from .varint import decode_integer


def decode_dynamic_table_size_update(data: bytes, pos: int) -> (int, int):
    """
    Decode a dynamic table size update instruction from the data starting at pos.

    Args:
        data (bytes): The QPACK header block data.
        pos (int): The current position in the data.

    Returns:
        (new_max_size, bytes_consumed): A tuple containing the updated maximum
                                        dynamic table size and the number of bytes consumed.

    Raises:
        ValueError: If the instruction does not have the correct prefix or is malformed.
    """
    if pos >= len(data):
        raise ValueError("Insufficient data for dynamic table size update.")
    first_byte = data[pos]
    # Check for the 3-bit prefix '001'
    if (first_byte >> 5) != 0b001:
        raise ValueError("Not a dynamic table size update instruction.")
    new_max_size, n = decode_integer(data[pos:], 5)
    return new_max_size, n
