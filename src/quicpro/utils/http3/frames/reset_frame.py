"""
Production-Ready RESET Frame Handler

Frame Format:
  - 4 bytes: stream_id (big-endian)
  - 4 bytes: error_code (big-endian)
"""

import struct
from pydantic import BaseModel, ValidationError

class ResetFrame(BaseModel):
    stream_id: int
    error_code: int

def handle_reset_frame(payload: bytes) -> bytes:
    if len(payload) < 8:
        raise ValueError("Payload too short for RESET frame.")
    stream_id = int.from_bytes(payload[:4], byteorder="big")
    error_code = int.from_bytes(payload[4:8], byteorder="big")
    try:
        frame = ResetFrame(stream_id=stream_id, error_code=error_code)
    except ValidationError as e:
        raise ValueError(f"Validation error in RESET frame: {e}") from e
    return f"RESET({frame.stream_id},{frame.error_code})".encode("utf-8")
