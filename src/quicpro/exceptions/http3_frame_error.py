"""
Module for errors in HTTP/3 frame extraction and validation.
"""

class HTTP3FrameError(Exception):
    """
    Custom exception for HTTP/3 frame extraction and validation errors.
    """
    def __init__(self, message: str = "HTTP/3 frame error"):
        super().__init__(message)
