"""
Module: settings.py

Encapsulates HTTP/3 connection settings negotiated between a client and a server.
This refined version provides robust error handling and supports conversion from/to a dictionary.
"""

from typing import Any, Dict


class HTTP3Settings:
    """
    Encapsulates HTTP/3 connection settings.
    
    Attributes:
        qpack_max_table_capacity (int): Maximum table capacity for QPACK header compression.
        qpack_blocked_streams (int): Maximum number of blocked streams.
        max_header_list_size (int): Maximum allowed header list size.
    """

    def __init__(
        self,
        qpack_max_table_capacity: int = 4096,
        qpack_blocked_streams: int = 100,
        max_header_list_size: int = 16384,
    ) -> None:
        self.qpack_max_table_capacity = qpack_max_table_capacity
        self.qpack_blocked_streams = qpack_blocked_streams
        self.max_header_list_size = max_header_list_size

    def encode(self) -> bytes:
        """
        Encode the settings into bytes.
        This example uses a simple comma-separated key=value format.
        
        Returns:
            bytes: The encoded settings.
        """
        # Create a sorted dictionary for consistent encoding order.
        settings: Dict[str, Any] = {
            "qpack_max_table_capacity": self.qpack_max_table_capacity,
            "qpack_blocked_streams": self.qpack_blocked_streams,
            "max_header_list_size": self.max_header_list_size,
        }
        # Encode as key=value pairs separated by commas.
        settings_str = ",".join(f"{key}={value}" for key, value in sorted(settings.items()))
        return settings_str.encode("utf-8")

    @classmethod
    def decode(cls, data: bytes) -> "HTTP3Settings":
        """
        Decode HTTP/3 settings from bytes.
        
        Args:
            data (bytes): The encoded settings.
            
        Returns:
            HTTP3Settings: The decoded HTTP/3 settings instance.
            
        Raises:
            ValueError: if a settings value cannot be converted to int.
        """
        settings_str = data.decode("utf-8").strip()
        settings: Dict[str, int] = {}
        if settings_str:
            for pair in settings_str.split(","):
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    try:
                        settings[key.strip()] = int(value.strip())
                    except ValueError as e:
                        raise ValueError(f"Invalid value for setting '{key}': {value}") from e
        return cls(
            qpack_max_table_capacity=settings.get("qpack_max_table_capacity", 4096),
            qpack_blocked_streams=settings.get("qpack_blocked_streams", 100),
            max_header_list_size=settings.get("max_header_list_size", 16384)
        )

    def to_dict(self) -> Dict[str, int]:
        """
        Return the settings as a dictionary.
        """
        return {
            "qpack_max_table_capacity": self.qpack_max_table_capacity,
            "qpack_blocked_streams": self.qpack_blocked_streams,
            "max_header_list_size": self.max_header_list_size,
        }

    def __repr__(self) -> str:
        return (
            f"<HTTP3Settings "
            f"qpack_max_table_capacity={self.qpack_max_table_capacity}, "
            f"qpack_blocked_streams={self.qpack_blocked_streams}, "
            f"max_header_list_size={self.max_header_list_size}>"
        )
