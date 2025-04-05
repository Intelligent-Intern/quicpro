"""
Production-Grade QPACK Encoder

This module implements a production-ready QPACK encoder for HTTP/3 header compression.
It supports:
  - Variable-length integer encoding.
  - Header field indexing with both a static table and a production-grade dynamic table.
  - Literal header field encoding with Huffman encoding (using a production-ready Huffman encoder).
  - Optional round-trip audit verification to ensure that headers encode and decode correctly.
  
The API is designed for production use; no "simulate" keyword is accepted.
"""

import logging
import hashlib
from typing import Dict, Tuple

from .varint import encode_integer
from .static_table import STATIC_TABLE
from .dynamic_table import DynamicTable
from .huffman import huffman_encode
from .decoder import QPACKDecoder

logger = logging.getLogger(__name__)


def _calculate_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class QPACKEncoder:
    def __init__(self, max_dynamic_table_size: int = 4096, auditing: bool = False) -> None:
        """
        Initialize the QPACKEncoder.

        Args:
            max_dynamic_table_size (int): Maximum capacity (in octets) for the dynamic table.
            auditing (bool): Enable round-trip audit verification.
        """
        self.auditing = auditing
        self.dynamic_table = DynamicTable(max_dynamic_table_size)
        if self.auditing:
            logger.info("QPACK Encoder auditing is ENABLED.")

    def _find_header_field(self, name: str, value: str) -> Tuple[bool, int]:
        """
        Search for a header field in the static and dynamic tables.

        Returns:
            Tuple[bool, int]: (True, index) if the header is found (1-based index);
                              (False, 0) if not found.
        """
        normalized_name = name.lower()
        # Search in the static table.
        for idx, (n, v) in enumerate(STATIC_TABLE, start=1):
            if n.lower() == normalized_name and v == value:
                logger.debug("Found header [%s: %s] in static table at index %d", name, value, idx)
                return True, idx
        # Search in the dynamic table.
        base = len(STATIC_TABLE)
        for idx, (n, v) in enumerate(self.dynamic_table.entries, start=1):
            if n.lower() == normalized_name and v == value:
                logger.debug("Found header [%s: %s] in dynamic table at index %d", name, value, base + idx)
                return True, base + idx
        return False, 0

    def _encode_literal(self, name: str, value: str, representation_flag: int = 0x00) -> bytes:
        """
        Encode a literal header field.

        Args:
            name (str): Header field name.
            value (str): Header field value.
            representation_flag (int): Flag indicating the literal representation type.
                                       0x00 for incremental indexing, 0x10 for never-indexed.
        
        Returns:
            bytes: The encoded literal header field.
        """
        encoded = bytearray([representation_flag])
        try:
            encoded_name = huffman_encode(name)
        except Exception as e:
            logger.error("Huffman encoding failed for header name '%s': %s", name, e)
            raise
        encoded += encode_integer(len(encoded_name), 5)
        encoded += encoded_name
        try:
            encoded_value = huffman_encode(value)
        except Exception as e:
            logger.error("Huffman encoding failed for header value '%s': %s", value, e)
            raise
        encoded += encode_integer(len(encoded_value), 7)
        encoded += encoded_value
        logger.debug("Encoded literal header [%s: %s] with flag 0x%02x (name: %d bytes, value: %d bytes)",
                     name, value, representation_flag, len(encoded_name), len(encoded_value))
        return bytes(encoded)

    def encode(self, headers: Dict[str, str]) -> bytes:
        """
        Encode a dictionary of HTTP headers into a QPACK header block.

        Args:
            headers (Dict[str, str]): The headers to encode.

        Returns:
            bytes: QPACK header block with a 2-byte big-endian length prefix.
        """
        header_block = bytearray()
        for name, value in headers.items():
            # Attempt to find the header in static or dynamic table.
            found, index = self._find_header_field(name, value)
            if found:
                # Encode the index using a 6-bit prefix.
                encoded_index = bytearray(encode_integer(index, 6))
                # Set the high-order bit for static table indexing.
                if index <= len(STATIC_TABLE):
                    encoded_index[0] |= 0x80
                    logger.debug("Encoded header [%s: %s] as static indexed (index=%d)", name, value, index)
                header_block.extend(encoded_index)
            else:
                # For sensitive headers, use never-indexed representation.
                if name.lower() in {"authorization", "cookie"}:
                    literal = self._encode_literal(name, value, representation_flag=0x10)
                else:
                    literal = self._encode_literal(name, value, representation_flag=0x00)
                    # Add to dynamic table for future reference.
                    self.dynamic_table.add(name, value)
                header_block.extend(literal)
        block_bytes = bytes(header_block)
        total_length = len(block_bytes)
        checksum = _calculate_checksum(block_bytes)
        logger.info("QPACK header block generated (length=%d, checksum=%s)", total_length, checksum)
        if self.auditing:
            decoder = QPACKDecoder()
            decoded_headers = decoder.decode(block_bytes)
            for key, orig_value in headers.items():
                dec_value = decoded_headers.get(key)
                if dec_value != orig_value:
                    logger.error("Round-trip audit failed for header '%s': original=%r, decoded=%r",
                                 key, orig_value, dec_value)
                    raise RuntimeError("QPACK round-trip verification failed during auditing.")
            logger.info("QPACK round-trip verification succeeded.")
        # Prepend the block length as a 2-byte big-endian integer.
        return total_length.to_bytes(2, byteorder="big") + block_bytes
