"""
Push frame module for HTTP/3.
Defines a PushFrame class used for server push.
"""

from .frame import HTTP3Frame
import struct


class PushFrame(HTTP3Frame):
    """
    Represents an HTTP/3 push frame used for server push.
    """
    FRAME_TYPE_PUSH = 0x05  # Example constant for a push frame

    def __init__(self, promised_stream_id: int, payload: bytes) -> None:
        """
        Initialize a PushFrame.
        Args:
            promised_stream_id (int): The stream identifier that is being pushed.
            payload (bytes): The push frame payload (e.g. headers and data).
        """
        # Prefix the payload with a 4-byte big-endian promised stream ID.
        stream_id_bytes = struct.pack("!I", promised_stream_id)
        full_payload = stream_id_bytes + payload
        super().__init__(self.FRAME_TYPE_PUSH, full_payload)
        self.promised_stream_id = promised_stream_id
        self.push_payload = payload

    @classmethod
    def decode(cls, data: bytes) -> "PushFrame":
        """
        Decode bytes into a PushFrame instance.
        Args:
            data (bytes): The raw data containing a push frame.
        Returns:
            PushFrame: The decoded push frame.
        Raises:
            ValueError: If the frame type or payload length is invalid.
        """
        base_frame = HTTP3Frame.decode(data)
        if base_frame.frame_type != cls.FRAME_TYPE_PUSH:
            raise ValueError("Data does not represent a PUSH frame.")
        if len(base_frame.payload) < 4:
            raise ValueError(
                "Push frame payload too short; missing promised stream ID.")
        promised_stream_id = struct.unpack("!I", base_frame.payload[:4])[0]
        push_payload = base_frame.payload[4:]
        return cls(promised_stream_id, push_payload)

    def __repr__(self) -> str:
        return f"<PushFrame promised_stream_id={self.promised_stream_id} payload_length={len(self.push_payload)}>"
