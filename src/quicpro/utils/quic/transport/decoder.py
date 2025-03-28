"""
decoder.py - Decoder for QUIC transport parameters.

This module decodes binary data into transport parameters.
It expects a comma-separated key=value string.
"""


def decode_transport_parameters(data: bytes) -> dict:
    """
    Decode transport parameters from bytes.

    Args:
        data (bytes): Encoded transport parameters.

    Returns:
        dict: Decoded transport parameters.
    """
    payload = data.decode("utf-8")
    params = {}
    if payload:
        for item in payload.split(","):
            if "=" in item:
                key, value = item.split("=", 1)
                params[key] = value
    return params
