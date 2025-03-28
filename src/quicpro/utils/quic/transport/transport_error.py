"""
transport_error.py - Exceptions for QUIC transport layer.

Defines errors encountered during transport parameter processing and flow control.
"""


class TransportError(Exception):
    """
    Base exception for QUIC transport errors.
    """

    def __init__(self, message: str = "An error occurred in the QUIC transport layer"):
        super().__init__(message)
