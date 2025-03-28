"""
Module for HTTP status errors.
"""

class HTTPStatusError(Exception):
    """
    Exception raised when HTTP response indicates an error status.
    """
    def __init__(self, message: str = "HTTP status error"):
        super().__init__(message)
