"""
Production-Grade QPACK Decoder

This module decodes a QPACK header block into a dictionary of headers.
It supports both indexed fields (using a 6-bit prefix) and literal header fields.
Literal fields are decoded using Huffman decoding.
Dynamic table updates are handled minimally.
"""

from typing import Dict, List, Tuple

from .huffman import decode as huffman_decode
from .encoder import STATIC_TABLE, decode_integer  # Reuse the integer decoder

class QPACKDecoder:
    """
    Production-grade QPACK Decoder.
    
    Maintains a dynamic table and decodes header blocks produced by QPACKEncoder.
    """
    def __init__(self) -> None:
        self.dynamic_table: List[Tuple[str, str]] = []

    def _decode_literal(self, data: bytes, pos: int) -> Tuple[Tuple[str, str], int]:
        """
        Decode a literal header field starting at position pos.
        
        Expected format:
          • 1 flag byte (0x00)
          • Name: length encoded with a 5-bit prefix, then Huffman-encoded bytes.
          • Value: length with a 7-bit prefix, then Huffman-encoded bytes.
        
        Returns a tuple ((name, value), bytes_consumed).
        """
        start = pos
        flag = data[pos]
        pos += 1  # Skip flag
        name_length, consumed = decode_integer(data[pos:], 5)
        pos += consumed
        name_encoded = data[pos: pos + name_length]
        pos += name_length
        name = huffman_decode(name_encoded)
        value_length, consumed = decode_integer(data[pos:], 7)
        pos += consumed
        value_encoded = data[pos: pos + value_length]
        pos += value_length
        value = huffman_decode(value_encoded)
        return (name, value), (pos - start)

    def decode(self, header_block: bytes) -> Dict[str, str]:
        """
        Decode a QPACK header block.
        
        Returns a dict mapping header names to values.
        """
        headers: Dict[str, str] = {}
        pos = 0
        total = len(header_block)
        while pos < total:
            b = header_block[pos]
            if b & 0x80:  # Indexed representation
                # Remove high-bit and decode index using 6-bit prefix.
                index, consumed = decode_integer(bytes([b & 0x7F]) + header_block[pos+1:], 6)
                pos += consumed
                total_static = len(STATIC_TABLE)
                if index <= total_static:
                    name, value = STATIC_TABLE[index - 1]
                    headers[name] = value
                else:
                    dynamic_index = index - total_static
                    if 0 < dynamic_index <= len(self.dynamic_table):
                        name, value = self.dynamic_table[dynamic_index - 1]
                        headers[name] = value
                    else:
                        raise ValueError(f"Invalid index {index} in QPACK decoding.")
            else:
                literal, consumed = self._decode_literal(header_block, pos)
                pos += consumed
                name, value = literal
                headers[name] = value
                self.dynamic_table.insert(0, (name, value))
            # Continue until block fully processed.
        return headers
"""
Production-Grade QPACK Decoder

This module decodes a QPACK header block into a dictionary of headers.
It supports both indexed header field representations and literal header fields.
Literal fields are decoded using Huffman decoding.

Dynamic table updates are handled in a basic form.
"""

from typing import Dict, List, Tuple

from .huffman import huffman_decode
from .encoder import STATIC_TABLE, encode_integer  # We'll reuse decode_integer from our huffman module
                                                    # if not provided here, assume it is imported elsewhere.

# For simplicity, we reimplement decode_integer here:
def decode_integer(data: bytes, prefix_bits: int) -> Tuple[int, int]:
    """
    Decode an integer using QPACK's variable-length integer encoding.

    Args:
        data (bytes): Bytes to decode from.
        prefix_bits (int): Number of bits in the first byte used for the integer.
    
    Returns:
        A tuple (value, bytes_consumed).
    """
    if not data:
        raise ValueError("No data available for integer decoding.")
    prefix_max = (1 << prefix_bits) - 1
    value = data[0] & prefix_max
    if value < prefix_max:
        return value, 1
    m = 0
    idx = 1
    while idx < len(data):
        b = data[idx]
        value += (b & 0x7F) << m
        m += 7
        idx += 1
        if b & 0x80 == 0:
            break
    else:
        raise ValueError("Incomplete integer encoding.")
    return value, idx

class QPACKDecoder:
    """
    Production-grade QPACK Decoder.

    Maintains a dynamic table and decodes header blocks produced by QPACKEncoder.
    """
    def __init__(self) -> None:
        self.dynamic_table: List[Tuple[str, str]] = []

    def _decode_literal(self, data: bytes, pos: int) -> Tuple[Tuple[str, str], int]:
        """
        Decode a literal header field starting at position pos.

        Expected literal format (simplified):
          • 1 flag byte (0x00 for literal with incremental indexing)
          • Name: length with variable-length integer using a 5-bit prefix,
              followed by Huffman-encoded name bytes.
          • Value: length with variable-length integer using a 7-bit prefix,
              followed by Huffman-encoded value bytes.

        Returns:
            A tuple ((name, value), bytes_consumed).
        """
        start = pos
        flag = data[pos]
        pos += 1  # Skip flag
        name_length, consumed = decode_integer(data[pos:], 5)
        pos += consumed
        name_encoded = data[pos: pos + name_length]
        pos += name_length
        name = huffman_decode(name_encoded)
        value_length, consumed = decode_integer(data[pos:], 7)
        pos += consumed
        value_encoded = data[pos: pos + value_length]
        pos += value_length
        value = huffman_decode(value_encoded)
        return (name, value), (pos - start)

    def decode(self, header_block: bytes) -> Dict[str, str]:
        """
        Decode a QPACK header block.
        
        Processes indexed fields (high bit set) and literals.
        Returns a dictionary mapping header names to values.
        """
        headers: Dict[str, str] = {}
        pos = 0
        total = len(header_block)
        while pos < total:
            b = header_block[pos]
            if b & 0x80:  # Indexed representation.
                # Remove the high bit and decode with a 6-bit prefix.
                index, consumed = decode_integer(bytes([b & 0x7F]) + header_block[pos+1:], 6)
                pos += consumed
                total_static = len(STATIC_TABLE)
                if index <= total_static:
                    name, value = STATIC_TABLE[index - 1]
                    headers[name] = value
                else:
                    dynamic_index = index - total_static
                    if 0 < dynamic_index <= len(self.dynamic_table):
                        name, value = self.dynamic_table[dynamic_index - 1]
                        headers[name] = value
                    else:
                        raise ValueError(f"Invalid index {index} in QPACK decoding.")
            else:
                literal, consumed = self._decode_literal(header_block, pos)
                pos += consumed
                name, value = literal
                headers[name] = value
                self.dynamic_table.insert(0, (name, value))
                # In production, ensure the dynamic table respects the table size limit.
            # Continue processing until the header block is fully consumed.
        return headers
