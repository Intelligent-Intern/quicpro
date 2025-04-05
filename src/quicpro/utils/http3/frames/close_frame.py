"""
Production-Ready CLOSE Frame Handler

Frame Format:
  - 4 bytes: error_code (big-endian)
  - remaining bytes: reason phrase (UTF-8 encoded)
"""

import struct
from pydantic import BaseModel, ValidationError

class CloseFrame(BaseModel):
    error_code: int
    reason: str

def handle_close_frame(payload: bytes) -> bytes:
    """
    Process a CLOSE frame payload.
    
    Args:
        payload (bytes): The CLOSE frame payload.
        
    Returns:
        bytes: A canonical representation of the CLOSE frame.
        
    Raises:
        ValueError: If the payload is invalid or cannot be parsed.
    """
    if len(payload) < 4:
        raise ValueError("Payload too short for CLOSE frame.")
    error_code = int.from_bytes(payload[:4], byteorder="big")
    try:
        reason = payload[4:].decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8 encoding in reason: {e}") from e
    try:
        frame = CloseFrame(error_code=error_code, reason=reason)
    except ValidationError as e:
        raise ValueError(f"Validation error in CLOSE frame: {e}") from e
    return f"CLOSE({frame.error_code},{frame.reason})".encode("utf-8")
