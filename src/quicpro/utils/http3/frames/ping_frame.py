"""
Production-Ready PING Frame Handler

Frame Format:
  - Payload: Optional UTF-8 encoded string (can be empty)
"""

import logging
from pydantic import BaseModel, ValidationError

class PingFrame(BaseModel):
    data: str = ""

def handle_ping_frame(payload: bytes) -> bytes:
    try:
        data = payload.decode("utf-8") if payload else ""
    except UnicodeDecodeError as e:
        raise ValueError(f"UTF-8 decode error in PING frame: {e}") from e
    try:
        frame = PingFrame(data=data)
    except ValidationError as e:
        raise ValueError(f"Validation error in PING frame: {e}") from e
    return f"PING({frame.data})".encode("utf-8")
