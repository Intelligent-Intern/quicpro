"""
Dynamic Table Management for QPACK

This module defines the DynamicTable class which manages header field entries.
It supports insertion and eviction based on the total octet consumption, following RFC 9204.
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def header_field_size(name: str, value: str) -> int:
    """
    Calculate the size of a header field as defined by RFC 9204.

    Size (in octets) = len(name) + len(value) + 32

    Args:
        name (str): Header field name.
        value (str): Header field value.

    Returns:
        int: The size in octets.
    """
    return len(name.encode("utf-8")) + len(value.encode("utf-8")) + 32


class DynamicTable:
    """
    Manages the dynamic table for QPACK header fields.

    It supports adding new header fields and evicts older entries if necessary
    to maintain the total size within the specified maximum.
    """

    def __init__(self, max_size: int = 4096) -> None:
        """
        Initialize the dynamic table.

        Args:
            max_size (int): Maximum allowed size in octets.
        """
        self.entries: List[Tuple[str, str]] = []
        self.max_size: int = max_size
        self.current_size: int = 0

    def _evict_entries(self, required_space: int) -> None:
        """
        Evict entries until the required space is available or the table is empty.

        Args:
            required_space (int): Additional space required.

        Raises:
            RuntimeError: If the header field size exceeds the maximum table size.
        """
        while (self.current_size + required_space > self.max_size) and self.entries:
            evicted_name, evicted_value = self.entries.pop()
            evicted_size = header_field_size(evicted_name, evicted_value)
            self.current_size -= evicted_size
            logger.debug("Evicted header [%s: %s] (size: %d) from dynamic table",
                         evicted_name, evicted_value, evicted_size)
        if required_space > self.max_size:
            raise RuntimeError(
                "Header field size exceeds maximum dynamic table size.")

    def add(self, name: str, value: str) -> None:
        """
        Add a new header field to the dynamic table, evicting older entries if necessary.

        Args:
            name (str): Header field name.
            value (str): Header field value.
        """
        size = header_field_size(name, value)
        self._evict_entries(size)
        self.entries.insert(0, (name, value))
        self.current_size += size
        logger.debug("Added header [%s: %s] (size: %d) to dynamic table (current size: %d)",
                     name, value, size, self.current_size)
