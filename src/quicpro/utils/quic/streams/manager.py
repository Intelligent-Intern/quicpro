"""
Module for managing QUIC streams.

This module provides classes for representing individual streams and a manager
for handling multiple streams.
"""

from typing import Optional
from .state import StreamState


class Stream:
    """
    Represents an individual QUIC stream with state and buffering.
    """

    def __init__(self, stream_id: int) -> None:
        """Initialize a Stream with a unique stream identifier."""
        self.stream_id = stream_id
        self.state = StreamState.IDLE
        self.buffer = b""

    def open(self) -> None:
        """Open the stream for data transmission."""
        self.state = StreamState.OPEN

    def close(self) -> None:
        """Close the stream."""
        self.state = StreamState.CLOSED

    def send_data(self, data: bytes) -> None:
        """
        Append data to the stream buffer.

        Args:
            data (bytes): The data to send.

        Raises:
            ValueError: If the stream is not open for sending data.
        """
        if self.state != StreamState.OPEN:
            raise ValueError("Stream is not open for sending data.")
        self.buffer += data


class StreamManager:
    """
    Manages multiple QUIC streams.
    """

    def __init__(self) -> None:
        """Initialize an empty stream manager."""
        self.streams = {}

    def create_stream(self, stream_id: int) -> Stream:
        """
        Create a new stream with the specified stream identifier.

        Args:
            stream_id (int): Unique identifier for the stream.

        Returns:
            Stream: The created stream instance.

        Raises:
            ValueError: If a stream with the given ID already exists.
        """
        if stream_id in self.streams:
            raise ValueError(f"Stream with ID {stream_id} already exists.")
        stream = Stream(stream_id)
        stream.open()
        self.streams[stream_id] = stream
        return stream

    def get_stream(self, stream_id: int) -> Optional[Stream]:
        """
        Retrieve a stream by its identifier.

        Args:
            stream_id (int): The stream identifier.

        Returns:
            Optional[Stream]: The stream if found; otherwise, None.
        """
        return self.streams.get(stream_id)

    def close_stream(self, stream_id: int) -> None:
        """
        Close the stream with the specified identifier.

        Args:
            stream_id (int): The stream identifier.
        """
        stream = self.get_stream(stream_id)
        if stream:
            stream.close()
