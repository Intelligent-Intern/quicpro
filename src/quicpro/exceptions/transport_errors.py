"""
Module for errors in the QUIC transport layer.
"""

class QuicTransportError(Exception):
    """
    Exception raised for issues within the QUIC transport layer, including transport parameters
    and flow control.
    """
    def __init__(self, message: str = "An error occurred in QUIC transport layer"):
        super().__init__(message)
