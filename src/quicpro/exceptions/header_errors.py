"""
Module for errors encountered during QUIC header processing.
"""

class QuicHeaderError(Exception):
    """
    Exception raised for errors encountered during QUIC header processing.
    """
    def __init__(self, message: str = "An error occurred with the QUIC header"):
        super().__init__(message)
