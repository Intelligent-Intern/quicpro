"""
Production-Ready GOAWAY Frame Handler

Frame Format:
  - 4 bytes: last_stream_id (big-endian)
  - 4 bytes: error_code (big-endian)
  - Remaining bytes: reason (UTF-8 encoded)
"""

import struct
from pydantic import BaseModel, ValidationError

class GoAwayFrame(BaseModel):
    last_stream_id: int
    error_code: int
    reason: str

def handle_goaway_frame(payload: bytes) -> bytes:
    if len(payload) < 8:
        raise ValueError("Payload too short for GOAWAY frame.")
    last_stream_id = int.from_bytes(payload[:4], byteorder="big")
    error_code = int.from_bytes(payload[4:8], byteorder="big")
    try:
        reason = payload[8:].decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"UTF-8 decode error in GOAWAY frame: {e}") from e
    try:
        frame = GoAwayFrame(last_stream_id=last_stream_id, error_code=error_code, reason=reason)
    except ValidationError as e:
        raise ValueError(f"Validation error in GOAWAY frame: {e}") from e
    return f"GOAWAY({frame.last_stream_id},{frame.error_code},{frame.reason})".encode("utf-8")
