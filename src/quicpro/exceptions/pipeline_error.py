"""
Module for pipeline errors.
"""

class PipelineError(Exception):
    """
    Base exception for pipeline errors.
    """
    def __init__(self, message: str = "Pipeline error"):
        super().__init__(message)
