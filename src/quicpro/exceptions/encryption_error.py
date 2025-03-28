"""
Module for errors during packet encryption.
"""

class EncryptionError(Exception):
    """
    Exception raised during packet encryption failures.
    """
    def __init__(self, message: str = "Encryption failed"):
        super().__init__(message)
