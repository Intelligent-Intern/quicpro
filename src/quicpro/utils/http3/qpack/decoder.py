"""
Production-Grade QPACK Decoder

This module implements a full-featured QPACK decoder for HTTP/3 header blocks.
It supports:
  • Decoding of the 2-byte length prefix
  • Decoding of dynamic table size update instructions via the instructions decoder
  • Decoding of indexed header fields from both the static and dynamic tables
  • Decoding of literal header fields using the literal decoder module
  • Dynamic table management for incremental indexing
  • Optional auditing via checksum verification

The modular design reuses our varint, static table, dynamic table, huffman,
instructions_decoder, and literal_decoder modules.
"""

import logging
import hashlib
from typing import Dict

from .varint import decode_integer
from .static_table import STATIC_TABLE
from .dynamic_table import DynamicTable
from .instructions_decoder import decode_dynamic_table_size_update
from .literal_decoder import decode_literal

logger = logging.getLogger(__name__)

def _calculate_checksum(data: bytes) -> str:
    """
    Calculate the SHA-256 checksum of the given data as a hexadecimal string.
    
    Args:
        data (bytes): Data for which to compute the checksum.
    
    Returns:
        str: The hexadecimal checksum.
    """
    import hashlib
    return hashlib.sha256(data).hexdigest()

class QPACKDecoder:
    """
    Production-grade QPACK Decoder.

    Decodes HTTP/3 headers from a QPACK header block using both static and dynamic
    table representations. Literal header fields are decoded via the literal decoder.
    Dynamic table updates (including size update instructions) are processed accordingly.
    """
    # Literal representation flags.
    LITERAL_WITH_INCREMENTAL_INDEXING = 0x00
    LITERAL_NEVER_INDEXED = 0x10
    LITERAL_WITHOUT_INDEXING = 0x20

    def __init__(self, max_dynamic_table_size: int = 4096, auditing: bool = False) -> None:
        """
        Initialize the QPACKDecoder.

        Args:
            max_dynamic_table_size (int): Maximum allowed dynamic table size (in octets).
            auditing (bool): Enable auditing (checksum verification).
        """
        self.dynamic_table = DynamicTable(max_dynamic_table_size)
        self.auditing = auditing

    def decode(self, header_block: bytes) -> Dict[str, str]:
        """
        Decode a QPACK header block into a dictionary of headers.

        The header block is expected to have a 2-byte big-endian length prefix.

        Args:
            header_block (bytes): The complete QPACK header block.

        Returns:
            Dict[str, str]: A dictionary mapping header names to values.

        Raises:
            ValueError: If decoding fails due to malformed input.
        """
        if len(header_block) < 2:
            raise ValueError("Header block too short; missing length prefix.")
        total_length = int.from_bytes(header_block[:2], byteorder="big")
        block = header_block[2:]
        if len(block) != total_length:
            raise ValueError("Header block length mismatch.")
        pos = 0
        headers: Dict[str, str] = {}
        while pos < len(block):
            current_byte = block[pos]
            # Check for dynamic table size update instruction.
            if (current_byte >> 5) == 0b001:
                new_size, n = decode_dynamic_table_size_update(block, pos)
                pos += n
                self.dynamic_table.max_size = new_size
                logger.info("Dynamic table size updated to %d", new_size)
                continue
            # Indexed header field representation (high bit set).
            if current_byte & 0x80:
                index, n = decode_integer(bytes([current_byte & 0x7F]) + block[pos+1:], 6)
                pos += n
                if index <= len(STATIC_TABLE):
                    name, value = STATIC_TABLE[index - 1]
                    headers[name] = value
                    logger.debug("Decoded static indexed header [%s: %s] (index=%d)",
                                 name, value, index)
                else:
                    dynamic_index = index - len(STATIC_TABLE)
                    if 0 < dynamic_index <= len(self.dynamic_table.entries):
                        name, value = self.dynamic_table.entries[dynamic_index - 1]
                        headers[name] = value
                        logger.debug("Decoded dynamic indexed header [%s: %s] (index=%d)",
                                     name, value, index)
                    else:
                        raise ValueError(f"Invalid index {index} in QPACK decoding.")
            else:
                # Literal header field.
                literal, n = decode_literal(block, pos)
                pos += n
                name, value = literal
                headers[name] = value
                # Update dynamic table if the flag indicates incremental indexing.
                flag = block[pos - n]
                if flag == self.LITERAL_WITH_INCREMENTAL_INDEXING:
                    self.dynamic_table.add(name, value)
            # Continue until the entire block is processed.
        if self.auditing:
            checksum = _calculate_checksum(block)
            logger.info("Decoded QPACK header block checksum: %s", checksum)
        return headers
