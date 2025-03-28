"""
HTTP/3 Stream Model
This module defines the Stream class representing an individual HTTP/3 stream.
Each stream maintains a state, an internal data buffer, and an optional priority.
State values are simple strings ("open" and "closed") to meet test expectations.
"""
import logging
from typing import Optional, Union
from quicpro.utils.http3.streams.priority import StreamPriority

logger = logging.getLogger(__name__)


class Stream:
    """Represents an individual HTTP/3 stream with state and priority."""

    def __init__(self, stream_id: int) -> None:
        """Initialize the Stream with a unique stream_id."""
        self.stream_id = stream_id
        self.state: str = "idle"
        self.buffer: bytes = b""
        self.priority: Optional[StreamPriority] = None

    def open(self) -> None:
        """Open the stream for data transmission."""
        self.state = "open"
        logger.info("Stream %d opened.", self.stream_id)

    def close(self) -> None:
        """Close the stream and stop data transmission."""
        self.state = "closed"
        logger.info("Stream %d closed.", self.stream_id)

    def send_data(self, data: bytes) -> None:
        """Send data through the stream if it's open."""
        if self.state != "open":
            raise RuntimeError(
                f"Stream {self.stream_id} is not open for sending data.")
        self.buffer += data
        logger.info("Stream %d buffered %d bytes.", self.stream_id, len(data))

    def set_priority(self, priority: Union[int, StreamPriority, None]) -> None:
        """Set the priority of the stream."""
        if priority is not None:
            if isinstance(priority, int):
                priority = StreamPriority(priority)
            self.priority = priority
            logger.info("Stream %d assigned priority weight %s.",
                        self.stream_id, priority.weight)

