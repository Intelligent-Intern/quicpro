"""
Enumeration of possible HTTP/3 stream states.

This module defines the stream states using a standard Enum.
"""

from enum import Enum


class StreamState(Enum):
    """
    Defines the possible states of an HTTP/3 stream.
    """
    IDLE = "idle"
    OPEN = "open"
    HALF_CLOSED = "half_closed"
    CLOSED = "closed"
