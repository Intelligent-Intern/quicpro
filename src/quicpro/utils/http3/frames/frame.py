"""
Base frame module for HTTP/3.
Defines the base class for all HTTP/3 frames.
"""

import struct
import logging

logger = logging.getLogger(__name__)

class HTTP3Frame:
    """
    Base class for HTTP/3 frames.
    Each frame consists of a type and a payload.
    """

    def __init__(self, frame_type: int, payload: bytes) -> None:
        """
        Initialize the frame.
        Args:
            frame_type (int): The numeric type of this frame.
            payload (bytes): The frame payload.
        """
        self.frame_type = frame_type
        self.payload = payload

    def encode(self) -> bytes:
        """
        Encode the frame into bytes.
        For simplicity, this example uses a fixed header:
          - 1-byte frame type
          - 4-byte big-endian integer representing the length of the payload
          - followed by the payload bytes.
        Returns:
            bytes: The encoded frame.
        """
        length = len(self.payload)
        header = struct.pack("!BI", self.frame_type, length)
        return header + self.payload

    @classmethod
    def decode(cls, data: bytes) -> "HTTP3Frame":
        """
        Decode bytes into an HTTP3Frame instance.
        Expects at least 5 bytes (1 for type, 4 for length).
        Args:
            data (bytes): The raw data containing a frame.
        Returns:
            HTTP3Frame: The decoded frame.
        Raises:
            ValueError: If data is too short or incomplete.
        """
        if len(data) < 5:
            raise ValueError("Data too short for an HTTP/3 frame header.")
        # Unpack header: 1-byte frame type and 4-byte payload length.
        frame_type, length = struct.unpack("!BI", data[:5])
        if len(data) < 5 + length:
            raise ValueError("Incomplete frame payload.")
        payload = data[5:5+length]
        logger.debug("Decoded HTTP3Frame: type=%d, length=%d", frame_type, length)
        return cls(frame_type, payload)

    def __repr__(self) -> str:
        return f"<HTTP3Frame type={self.frame_type} payload_length={len(self.payload)}>"
