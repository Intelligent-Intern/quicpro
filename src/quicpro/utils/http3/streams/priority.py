"""
HTTP/3 Stream Priority Module

This module defines a production-ready priority mechanism for HTTP/3 streams.
Streams may be assigned a numerical priority and an optional dependency, which
can be used by the stream manager and scheduler to order transmission.
"""

from dataclasses import dataclass, field

@dataclass(order=True)
class StreamPriority:
    """
    Represents the priority for an HTTP/3 stream.

    Attributes:
      weight (int): Should be in the range 1 (lowest priority) to 256 (highest priority). 
                    Lower numerical values can be interpreted as either higher or lower priority
                    depending on your chosen policy; here we assume 1 is highest.
      dependency (int): The stream ID this stream depends on; 0 means no dependency.
    """
    weight: int = field(default=16, compare=True)
    dependency: int = field(default=0, compare=False)

    def __post_init__(self) -> None:
        if not (1 <= self.weight <= 256):
            raise ValueError("Weight must be between 1 and 256")
