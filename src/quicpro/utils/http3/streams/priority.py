"""
HTTP/3 Stream Priority
This module defines the StreamPriority class, which encapsulates the priority
of an HTTP/3 stream. The priority is represented as a weight, where a lower
weight indicates higher priority. Valid weights range from 1 (highest) to 256
(lowest). A convenience method allows creation from a common PriorityLevel.
"""
from typing import Optional
from quicpro.utils.http3.streams.enum.priority_level import PriorityLevel


class StreamPriority:
    """
    Represents the priority of an HTTP/3 stream.
    A lower weight implies higher priority. The weight must be an integer between
    1 and 256.
    """

    def __init__(self, weight: int, dependency: Optional[int] = None) -> None:
        """
        Initialize a StreamPriority instance.

        Args:
            weight (int): The weight value (1 to 256).
            dependency (Optional[int]): Optional dependency information (ignored in our implementation).

        Raises:
            ValueError: If the weight is not within the valid range.
        """
        if not (1 <= weight <= 256):
            raise ValueError("Weight must be between 1 and 256.")
        self.weight: int = weight
        # dependency is accepted per full standard but currently unused
        self.dependency = dependency

    @classmethod
    def from_priority_level(cls, level: PriorityLevel) -> "StreamPriority":
        """
        Create a StreamPriority instance from a PriorityLevel enum value.

        Args:
            level (PriorityLevel): A member of the PriorityLevel enumeration.

        Returns:
            StreamPriority: An instance with the corresponding weight.
        """
        return cls(weight=level.value)

    def __lt__(self, other: "StreamPriority") -> bool:
        return self.weight < other.weight

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, StreamPriority):
            return NotImplemented
        return self.weight == other.weight

    def __repr__(self) -> str:
        return f"<StreamPriority weight={self.weight}>"

