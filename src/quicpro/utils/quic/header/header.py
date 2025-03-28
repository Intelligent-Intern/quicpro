"""
Header module for QUIC protocol.

This module defines the Header class that encapsulates header fields with
validation, encoding, and decoding functionalities.
"""

from .base import encode_varint, decode_varint
from .definitions import DEFAULT_HEADER

class Header:
    """
    Header class for QUIC protocol.

    This class encapsulates header fields and provides methods for validating,
    encoding, and decoding the header.
    """
    def __init__(self, **fields):
        """
        Initialize the header with default values and update with provided fields.
        """
        self.fields = DEFAULT_HEADER.copy()
        self.fields.update(fields)
        self.validate()

    def validate(self):
        """Validate that required header fields are present."""
        if "version" not in self.fields:
            raise ValueError("Header must include a 'version' field.")
        if "type" not in self.fields:
            raise ValueError("Header must include a 'type' field.")
        if "connection_id" not in self.fields:
            raise ValueError("Header must include a 'connection_id' field.")
        # Additional validation per QUIC spec can be added.

    def encode(self) -> bytes:
        """
        Encode the header into bytes.

        Returns:
            bytes: The encoded header.
        """
        payload = ";".join(f"{k}={self.fields[k]}" for k in sorted(self.fields))
        payload_bytes = payload.encode("utf-8")
        length_bytes = encode_varint(len(payload_bytes))
        return length_bytes + payload_bytes

    @classmethod
    def decode(cls, data: bytes):
        """
        Decode header bytes into a Header instance.

        Args:
            data (bytes): The encoded header.

        Returns:
            Header: The decoded header instance.
        """
        total_length, consumed = decode_varint(data)
        payload_bytes = data[consumed:consumed + total_length]
        payload_str = payload_bytes.decode("utf-8")
        fields = {}
        for field in payload_str.split(";"):
            if "=" in field:
                key, val = field.split("=", 1)
                fields[key] = val
        return cls(**fields)

    def __str__(self):
        return f"Header({self.fields})"

    def __repr__(self):
        return self.__str__()
