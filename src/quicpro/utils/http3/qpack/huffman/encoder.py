"""
QPACK Huffman Encoder for HTTP/3.

This module encodes strings using the QPACK static Huffman table.
It accumulates bits for each character’s code and flushes the resulting bitstream into bytes,
padding the final octet with all ones as required by the specification.
"""

from typing import ByteString
from .constants import HUFFMAN_TABLE

def encode(data: str) -> bytes:
    """
    Encode a string using the QPACK/HPACK Huffman algorithm.
    
    Args:
        data (str): The input string.
        
    Returns:
        bytes: The Huffman encoded bytes.
    """
    bit_buffer = 0
    bit_count = 0
    output = bytearray()
    
    for ch in data:
        symbol = ord(ch)
        try:
            code, nbits = HUFFMAN_TABLE[symbol]
        except KeyError:
            raise ValueError(f"Symbol {ch} (code {symbol}) not in Huffman table.")
        bit_buffer = (bit_buffer << nbits) | code
        bit_count += nbits
        while bit_count >= 8:
            bit_count -= 8
            byte = (bit_buffer >> bit_count) & 0xFF
            output.append(byte)
    if bit_count > 0:
        # Pad the remaining bits with ones (all ones padding per spec)
        pad = (1 << (8 - bit_count)) - 1
        output.append(((bit_buffer << (8 - bit_count)) & 0xFF) | pad)
    return bytes(output)
