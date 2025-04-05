"""
Production-Ready CONTROL Frame Handler

Frame Format:
  - 1 byte: control_code (unsigned integer)
  - remaining bytes: control_data (UTF-8 encoded string)
"""

import struct
from pydantic import BaseModel, ValidationError

class ControlFrame(BaseModel):
    control_code: int
    data: str

def handle_control_frame(payload: bytes) -> bytes:
    """
    Process a CONTROL frame payload.
    
    Args:
        payload (bytes): The CONTROL frame payload.
        
    Returns:
        bytes: A canonical representation of the CONTROL frame.
        
    Raises:
        ValueError: If the payload is invalid or cannot be parsed.
    """
    if len(payload) < 1:
        raise ValueError("Payload too short for CONTROL frame.")
    control_code = payload[0]
    try:
        data = payload[1:].decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"Invalid UTF-8 encoding in CONTROL frame: {e}") from e
    try:
        frame = ControlFrame(control_code=control_code, data=data)
    except ValidationError as e:
        raise ValueError(f"Validation error in CONTROL frame: {e}") from e
    return f"CONTROL({frame.control_code},{frame.data})".encode("utf-8")
