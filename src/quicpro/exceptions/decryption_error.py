"""
Module for errors during the decryption process.
"""

class DecryptionError(Exception):
    """
    Exception raised during the decryption process on the receiver side.
    """
    def __init__(self, message: str = "Decryption failed"):
        super().__init__(message)
