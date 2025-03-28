"""
Encoder module for QUIC transport parameters.
Converts a dictionary into a comma-separated key=value string encoded in UTF-8.
"""


def encode_transport_parameters(params: dict) -> bytes:
    """
    Encode transport parameters into bytes.
    """
    payload = ",".join(f"{k}={v}" for k, v in sorted(params.items()))
    return payload.encode("utf-8")
