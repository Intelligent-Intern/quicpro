"""
Module for errors in QUIC stream processing.
"""

class QuicStreamError(Exception):
    """
    Exception raised for errors encountered during QUIC stream management.
    """
    def __init__(self, message: str = "An error occurred in QUIC stream processing"):
        super().__init__(message)
