"""
Module for errors during the decoding process.
"""

class DecodingError(Exception):
    """
    Exception raised during the decoding process on the receiver side.
    """
    def __init__(self, message: str = "Decoding error"):
        super().__init__(message)
