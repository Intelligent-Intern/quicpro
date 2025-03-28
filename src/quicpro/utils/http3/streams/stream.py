"""
HTTP/3 Stream Model

This module defines the Stream class representing an individual HTTP/3 stream.
Each stream maintains its state, an internal data buffer, and an optional priority.
"""

import threading
import logging
from typing import Optional

from quicpro.utils.http3.streams.enum.stream_state import StreamState
from quicpro.utils.http3.streams.priority import StreamPriority

logger = logging.getLogger(__name__)


class Stream:
    """
    Represents an individual HTTP/3 stream.

    This domain model encapsulates the state, data buffering, and optional priority
    of a stream. It provides thread-safe methods for sending and receiving data.
    """
    def __init__(self, stream_id: int) -> None:
        """
        Initialize a new Stream instance.

        Args:
            stream_id (int): Unique identifier for the stream.
        """
        self.stream_id: int = stream_id
        self.state: StreamState = StreamState.IDLE
        self.buffer: bytearray = bytearray()
        self.lock = threading.Lock()
        self.priority: Optional[StreamPriority] = None

    def open(self) -> None:
        """
        Open the stream for data transmission.

        Transitions the stream state from IDLE to OPEN.
        Logs a warning if the stream is already opened or closed.
        """
        with self.lock:
            if self.state != StreamState.IDLE:
                logger.warning("Stream %d already opened or closed", self.stream_id)
                return
            self.state = StreamState.OPEN
            logger.info("Stream %d opened", self.stream_id)

    def close(self) -> None:
        """
        Close the stream.

        Sets the stream state to CLOSED.
        """
        with self.lock:
            if self.state == StreamState.CLOSED:
                return
            self.state = StreamState.CLOSED
            logger.info("Stream %d closed", self.stream_id)

    def send_data(self, data: bytes) -> None:
        """
        Append data to the stream's buffer.

        Args:
            data (bytes): Data to be buffered.

        Raises:
            RuntimeError: If the stream is not in the OPEN state.
        """
        with self.lock:
            if self.state != StreamState.OPEN:
                raise RuntimeError(
                    f"Stream {self.stream_id} is not open for sending data."
                )
            self.buffer.extend(data)
            logger.debug("Stream %d buffered %d bytes", self.stream_id, len(data))

    def receive_data(self) -> bytes:
        """
        Retrieve and clear the buffered data from the stream.

        Returns:
            bytes: The buffered data.
        """
        with self.lock:
            data = bytes(self.buffer)
            self.buffer.clear()
            logger.debug("Stream %d returned %d bytes of data", self.stream_id, len(data))
            return data

    def set_priority(self, priority: StreamPriority) -> None:
        """
        Set the priority for this stream.

        Args:
            priority (StreamPriority): Priority to assign.
        """
        with self.lock:
            self.priority = priority
            logger.info("Stream %d assigned priority with weight %d",
                        self.stream_id, priority.weight)
