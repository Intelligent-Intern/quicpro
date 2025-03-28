"""
Module for errors during QUIC packet processing.
"""

class QuicPacketError(Exception):
    """
    Exception raised for errors in QUIC packet encoding, decoding, or retransmission.
    """
    def __init__(self, message: str = "An error occurred in QUIC packet processing"):
        super().__init__(message)
