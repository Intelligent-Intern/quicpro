"""
Module for transmission errors.
"""

class TransmissionError(Exception):
    """
    Exception raised during network transmission issues.
    """
    def __init__(self, message: str = "Transmission error"):
        super().__init__(message)
