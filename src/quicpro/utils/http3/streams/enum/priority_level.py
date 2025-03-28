"""
Defines common priority levels for HTTP/3 streams.

This module provides an enumeration of common priority levels that can be used to
assign a default weight to a stream. Lower weight indicates higher priority.
"""

from enum import Enum


class PriorityLevel(Enum):
    """
    Enumeration of common priority levels.
    """
    HIGH = 1
    NORMAL = 128
    LOW = 256
