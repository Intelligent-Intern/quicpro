"""
Production-Ready UNKNOWN Frame Handler

Frame Format:
  - Payload: Raw bytes whose structure is unknown.
"""

import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class UnknownFrame(BaseModel):
    payload: bytes

def handle_unknown_frame(payload: bytes) -> bytes:
    try:
        frame = UnknownFrame(payload=payload)
    except ValidationError as e:
        raise ValueError(f"Validation error in UNKNOWN frame: {e}") from e
    return f"UNKNOWN({frame.payload.hex()})".encode("utf-8")
