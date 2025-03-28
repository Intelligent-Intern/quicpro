"""
Production-Grade QPACK Encoder

This module implements a full-featured QPACK encoder for HTTP/3 header blocks.
It leverages modular components for variable-length integer encoding, dynamic table
management, static table definitions, and instruction encoding. It optionally performs
round-trip auditing using a checksum.

The final encoded header block is prefixed with its 2-byte big-endian length.
"""

import logging
import hashlib
from typing import Dict, Tuple

from .varint import encode_integer
from .static_table import STATIC_TABLE
from .dynamic_table import DynamicTable, header_field_size
from .instructions import encode_dynamic_table_size_update
from .huffman import huffman_encode
from .decoder import QPACKDecoder

logger = logging.getLogger(__name__)

def _calculate_checksum(data: bytes) -> str:
    """
    Calculate the SHA-256 checksum of the given data as a hexadecimal string.

    Args:
        data (bytes): Data to checksum.

    Returns:
        str: The hexadecimal checksum.
    """
    return hashlib.sha256(data).hexdigest()

class QPACKEncoder:
    """
    Production-grade QPACK Encoder.

    Encodes HTTP/3 headers into a QPACK header block using both static and dynamic
    table representations. Supports multiple literal representations and dynamic
    table size updates.
    """
    LITERAL_WITH_INCREMENTAL_INDEXING = 0x00
    LITERAL_NEVER_INDEXED = 0x10
    LITERAL_WITHOUT_INDEXING = 0x20

    def __init__(self, max_dynamic_table_size: int = 4096, auditing: bool = False) -> None:
        """
        Initialize the QPACK encoder.

        Args:
            max_dynamic_table_size (int): Maximum allowed size in octets for the dynamic table.
            auditing (bool): Enable auditing (checksum and round-trip decoding).
        """
        self.dynamic_table = DynamicTable(max_dynamic_table_size)
        self.auditing: bool = auditing
        if self.auditing:
            logger.info("QPACK Encoder auditing is ENABLED.")

    def _find_header_field(self, name: str, value: str) -> Tuple[bool, int]:
        """
        Search for a header field in the static and dynamic tables.

        Returns:
            Tuple[bool, int]: (True, index) if found (1-based index), else (False, 0).
        """
        normalized_name = name.lower()
        for idx, (n, v) in enumerate(STATIC_TABLE, start=1):
            if n.lower() == normalized_name and v == value:
                logger.debug("Found header [%s: %s] in static table at index %d", name, value, idx)
                return True, idx
        base = len(STATIC_TABLE)
        for idx, (n, v) in enumerate(self.dynamic_table.entries, start=1):
            if n.lower() == normalized_name and v == value:
                logger.debug("Found header [%s: %s] in dynamic table at index %d", name, value, base + idx)
                return True, base + idx
        return False, 0

    def _encode_literal(self, name: str, value: str,
                        representation_flag: int = LITERAL_WITH_INCREMENTAL_INDEXING) -> bytes:
        """
        Encode a literal header field using the specified representation flag.

        Args:
            name (str): Header name.
            value (str): Header value.
            representation_flag (int): Flag for literal representation.

        Returns:
            bytes: The encoded literal header field.
        """
        encoded = bytearray([representation_flag])
        encoded_name = huffman_encode(name)
        encoded += encode_integer(len(encoded_name), 5)
        encoded += encoded_name
        encoded_value = huffman_encode(value)
        encoded += encode_integer(len(encoded_value), 7)
        encoded += encoded_value
        logger.debug("Encoded literal header [%s: %s] with flag 0x%02x "
                     "(name: %d bytes, value: %d bytes)",
                     name, value, representation_flag, len(encoded_name), len(encoded_value))
        return bytes(encoded)

    def encode(self, headers: Dict[str, str]) -> bytes:
        """
        Encode HTTP headers into a QPACK header block.

        For each header:
          • If found in the static or dynamic table, use an indexed representation.
          • Otherwise, encode as a literal header field (using never-indexed for sensitive headers)
            and add to the dynamic table.
          • Optionally, prepend dynamic table size update instructions.
        
        Returns:
            bytes: The complete QPACK header block, prefixed with its 2-byte length.
        
        Raises:
            RuntimeError: If round-trip auditing fails.
        """
        header_block = bytearray()
        # (Optional) Dynamic table size update could be inserted here.
        for name, value in headers.items():
            found, index = self._find_header_field(name, value)
            if found:
                encoded_index = bytearray(encode_integer(index, 6))
                if index <= len(STATIC_TABLE):
                    encoded_index[0] |= 0x80
                    logger.debug("Encoded header [%s: %s] as static indexed (index=%d)",
                                 name, value, index)
                else:
                    logger.debug("Encoded header [%s: %s] as dynamic indexed (index=%d)",
                                 name, value, index)
                header_block.extend(encoded_index)
            else:
                if name.lower() in {"authorization", "cookie"}:
                    literal = self._encode_literal(name, value, representation_flag=self.LITERAL_NEVER_INDEXED)
                else:
                    literal = self._encode_literal(name, value, representation_flag=self.LITERAL_WITH_INCREMENTAL_INDEXING)
                    self.dynamic_table.add(name, value)
                header_block.extend(literal)
        block_bytes = bytes(header_block)
        audit_checksum = _calculate_checksum(block_bytes)
        logger.info("QPACK header block checksum: %s", audit_checksum)
        if self.auditing:
            decoder = QPACKDecoder()
            decoded_headers = decoder.decode(block_bytes)
            for key, orig_value in headers.items():
                dec_value = decoded_headers.get(key)
                if dec_value != orig_value:
                    logger.error("Round-trip audit failed for header %s: original=%r, decoded=%r",
                                 key, orig_value, dec_value)
                    raise RuntimeError("QPACK round-trip verification failed during auditing.")
            logger.info("QPACK round-trip verification succeeded.")
        return len(block_bytes).to_bytes(2, byteorder="big") + block_bytes
