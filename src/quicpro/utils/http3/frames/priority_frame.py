"""
Production-Ready PRIORITY UPDATE Frame Handler

Frame Format:
  - 4 bytes: stream_id (big-endian)
  - 1 byte: updated_priority_weight (unsigned integer)
"""

import struct
from pydantic import BaseModel, ValidationError

class PriorityUpdateFrame(BaseModel):
    stream_id: int
    updated_priority_weight: int

def handle_priority_update_frame(payload: bytes) -> bytes:
    if len(payload) < 5:
        raise ValueError("Payload too short for PRIORITY UPDATE frame.")
    stream_id = int.from_bytes(payload[:4], byteorder="big")
    updated_priority_weight = payload[4]
    try:
        frame = PriorityUpdateFrame(stream_id=stream_id, updated_priority_weight=updated_priority_weight)
    except ValidationError as e:
        raise ValueError(f"Validation error in PRIORITY UPDATE frame: {e}") from e
    return f"PRIORITY_UPDATE({frame.stream_id},{frame.updated_priority_weight})".encode("utf-8")
