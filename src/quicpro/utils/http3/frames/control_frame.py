"""
Control frame module for HTTP/3.
Provides a ControlFrame class to represent control messages such as SETTINGS.
"""

from .frame import HTTP3Frame

class ControlFrame(HTTP3Frame):
    """
    Represents an HTTP/3 control frame.
    For example, a SETTINGS frame.
    """
    FRAME_TYPE_SETTINGS = 0x04  # Example constant for a SETTINGS frame.

    def __init__(self, settings: dict) -> None:
        """
        Initialize a ControlFrame with the provided settings.
        Args:
            settings (dict): A dictionary of HTTP/3 settings.
        """
        payload = self._encode_settings(settings)
        super().__init__(self.FRAME_TYPE_SETTINGS, payload)
        self.settings = settings

    @staticmethod
    def _encode_settings(settings: dict) -> bytes:
        """
        Encode the settings dictionary into bytes.
        In a full implementation, this should follow the HTTP/3 SETTINGS format.
        For this example, we simply join key=value pairs with commas.
        """
        settings_str = ",".join(f"{k}={v}" for k, v in settings.items())
        return settings_str.encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> "ControlFrame":
        """
        Decode bytes into a ControlFrame.
        Args:
            data (bytes): The raw data containing the control frame.
        Returns:
            ControlFrame: The decoded control frame.
        Raises:
            ValueError: If the frame type does not match SETTINGS.
        """
        base_frame = HTTP3Frame.decode(data)
        if base_frame.frame_type != cls.FRAME_TYPE_SETTINGS:
            raise ValueError("Data does not represent a SETTINGS control frame.")
        settings = cls._decode_settings(base_frame.payload)
        return cls(settings)

    @staticmethod
    def _decode_settings(data: bytes) -> dict:
        """
        Decode the settings from bytes.
        """
        settings_str = data.decode("utf-8")
        settings = {}
        for pair in settings_str.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                settings[key] = value
        return settings

    def __repr__(self) -> str:
        return f"<ControlFrame settings={self.settings}>"
