"""
Production-Ready ERROR Frame Handler

Frame Format:
  - 4 bytes: error_code (big-endian)
  - remaining bytes: error_message (UTF-8 encoded)
"""

import struct
from pydantic import BaseModel, ValidationError

class ErrorFrame(BaseModel):
    error_code: int
    error_message: str

def handle_error_frame(payload: bytes) -> bytes:
    """
    Process an ERROR frame payload.
    
    Args:
        payload (bytes): The payload of the ERROR frame.
        
    Returns:
        bytes: A canonical representation of the ERROR frame.
        
    Raises:
        ValueError: If the payload is invalid.
    """
    if len(payload) < 4:
        raise ValueError("Payload too short for ERROR frame.")
    error_code = int.from_bytes(payload[:4], byteorder="big")
    try:
        error_message = payload[4:].decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"UTF-8 decode error in ERROR frame: {e}") from e
    try:
        frame = ErrorFrame(error_code=error_code, error_message=error_message)
    except ValidationError as e:
        raise ValueError(f"Validation error in ERROR frame: {e}") from e
    return f"ERROR({frame.error_code},{frame.error_message})".encode("utf-8")