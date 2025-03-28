"""
Literal Header Field Decoder for QPACK

This module provides a function to decode a literal header field from a QPACK header block.
It handles the flag byte, variable-length integer encoded lengths for the header name and value,
and Huffman decoding of both.
"""

from typing import Tuple
from .varint import decode_integer
from .huffman import huffman_decode

def decode_literal(data: bytes, pos: int) -> Tuple[Tuple[str, str], int]:
    """
    Decode a literal header field starting at the given position.

    Expected format:
      • 1 flag byte (indicating the literal representation type)
      • Header name length encoded as a variable-length integer with a 5-bit prefix,
      • Huffman-encoded header name bytes,
      • Header value length encoded as a variable-length integer with a 7-bit prefix,
      • Huffman-encoded header value bytes.

    Args:
        data (bytes): The QPACK header block data.
        pos (int): The starting position for the literal header field.

    Returns:
        ((name, value), bytes_consumed): A tuple with the decoded header field and
                                          the number of bytes consumed.
    
    Raises:
        ValueError: If the data is incomplete or malformed.
    """
    start = pos
    if pos >= len(data):
        raise ValueError("Insufficient data for literal header field.")
    flag = data[pos]
    pos += 1  # Consume flag.
    # Decode header name length with a 5-bit prefix.
    name_length, n = decode_integer(data[pos:], 5)
    pos += n
    if pos + name_length > len(data):
        raise ValueError("Incomplete header name in literal field.")
    encoded_name = data[pos: pos + name_length]
    pos += name_length
    name = huffman_decode(encoded_name)
    # Decode header value length with a 7-bit prefix.
    value_length, n = decode_integer(data[pos:], 7)
    pos += n
    if pos + value_length > len(data):
        raise ValueError("Incomplete header value in literal field.")
    encoded_value = data[pos: pos + value_length]
    pos += value_length
    value = huffman_decode(encoded_value)
    return (name, value), (pos - start)
