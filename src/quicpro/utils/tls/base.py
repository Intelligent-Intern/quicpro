"""
Common Constants and Utility Functions for TLS Modules
This module provides foundational constants, logging setup, and cryptographically
secure utilities for TLS operations.
"""

import os
import logging

# TLS version constants
TLS_VERSION_1_2 = "TLSv1.2"
TLS_VERSION_1_3 = "TLSv1.3"

# Configure module-level logger with a stream handler and proper formatter.
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def log_tls_debug(message: str) -> None:
    """
    Log a debug-level message with a TLS-specific prefix.
    
    Args:
        message (str): The message to log.
    """
    logger.debug(f"[TLS] {message}")

def generate_random_bytes(n: int) -> bytes:
    """
    Generate cryptographically secure random bytes.
    
    Args:
        n (int): The number of bytes to generate.

    Returns:
        bytes: n random bytes.
    
    Raises:
        ValueError: If n is not a positive integer.
    """
    if n <= 0:
        raise ValueError("Number of random bytes must be positive.")
    return os.urandom(n)