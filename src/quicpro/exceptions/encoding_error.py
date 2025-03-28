"""
Module for errors during encoding.
"""

class EncodingError(Exception):
    """
    Exception raised when encoding of a message fails.
    """
    def __init__(self, message: str = "Encoding failed"):
        super().__init__(message)
