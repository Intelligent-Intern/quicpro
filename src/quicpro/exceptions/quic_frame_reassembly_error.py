"""
Module for errors during QUIC frame reassembly.
"""

class QUICFrameReassemblyError(Exception):
    """
    Exception raised during QUIC frame reassembly.
    """
    def __init__(self, message: str = "QUIC frame reassembly error"):
        super().__init__(message)
