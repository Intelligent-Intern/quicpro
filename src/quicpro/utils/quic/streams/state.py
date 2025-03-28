"""
Module defining the stream state enumeration for QUIC streams.

This module provides an Enum representing various states of a QUIC stream.
"""

from enum import Enum


class StreamState(Enum):
    """Enumeration of possible states for a QUIC stream."""
    IDLE = "idle"
    OPEN = "open"
    HALF_CLOSED_LOCAL = "half_closed_local"
    HALF_CLOSED_REMOTE = "half_closed_remote"
    CLOSED = "closed"
