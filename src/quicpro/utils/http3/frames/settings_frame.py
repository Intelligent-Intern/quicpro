"""
Production-Ready SETTINGS Frame Handler

Frame Format:
  - Payload: A UTF-8 encoded string representing settings in the format "key1=value1;key2=value2;..."
"""

import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class SettingsFrame(BaseModel):
    settings: dict

def parse_settings(payload_str: str) -> dict:
    settings = {}
    for pair in payload_str.split(";"):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"Invalid settings pair: {pair}")
        key, value = pair.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings

def handle_settings_frame(payload: bytes) -> bytes:
    if not payload:
        raise ValueError("Empty payload in SETTINGS frame.")
    try:
        payload_str = payload.decode("utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"UTF-8 decode error in SETTINGS frame: {e}") from e
    settings_dict = parse_settings(payload_str)
    try:
        frame = SettingsFrame(settings=settings_dict)
    except ValidationError as e:
        raise ValueError(f"Validation error in SETTINGS frame: {e}") from e
    return f"SETTINGS({frame.settings})".encode("utf-8")
