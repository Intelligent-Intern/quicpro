"""
Module for QUIC connection errors.
"""


class QuicConnectionError(Exception):
    """
    Exception raised for errors in QUIC connection operations.
    """

    def __init__(self, message: str = "An error occurred in QUIC connection"):
        super().__init__(message)
