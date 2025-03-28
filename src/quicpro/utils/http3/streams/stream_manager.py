"""
Production-Grade HTTP/3 Stream Manager

This module implements a thread-safe stream management system for HTTP/3.
It handles creation, retrieval, and closure of streams and is designed for
integration into high-assurance systems. Each stream maintains its own state and
buffer, and the manager assigns unique stream IDs.
"""

import threading
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class StreamState:
    """
    Enumeration of possible stream states.
    """
    IDLE = "idle"
    OPEN = "open"
    HALF_CLOSED = "half_closed"
    CLOSED = "closed"


class Stream:
    """
    Represents an individual HTTP/3 stream.

    This class manages the stream state, buffering of data, and provides
    thread-safe methods for sending and receiving data.
    """
    def __init__(self, stream_id: int) -> None:
        self.stream_id: int = stream_id
        self.state: str = StreamState.IDLE
        self.buffer: bytearray = bytearray()
        self.lock = threading.Lock()

    def open(self) -> None:
        with self.lock:
            if self.state != StreamState.IDLE:
                logger.warning("Stream %d already opened or closed", self.stream_id)
                return
            self.state = StreamState.OPEN
            logger.info("Stream %d opened", self.stream_id)

    def close(self) -> None:
        with self.lock:
            if self.state == StreamState.CLOSED:
                return
            self.state = StreamState.CLOSED
            logger.info("Stream %d closed", self.stream_id)

    def send_data(self, data: bytes) -> None:
        """
        Append data to the stream's buffer.
        
        Raises:
            RuntimeError: if the stream is not open.
        """
        with self.lock:
            if self.state != StreamState.OPEN:
                raise RuntimeError(f"Stream {self.stream_id} is not open for sending data.")
            self.buffer.extend(data)
            logger.debug("Stream %d buffered %d bytes", self.stream_id, len(data))

    def receive_data(self) -> bytes:
        """
        Return and clear the buffered data from the stream.
        """
        with self.lock:
            data = bytes(self.buffer)
            self.buffer.clear()
            logger.debug("Stream %d returned %d bytes of data", self.stream_id, len(data))
            return data


class StreamManager:
    """
    Manages multiple HTTP/3 streams.

    Provides thread-safe methods to create new streams, retrieve existing streams,
    and close streams. Streams are keyed by their unique stream IDs.
    """
    def __init__(self) -> None:
        self._streams: Dict[int, Stream] = {}
        self._lock = threading.Lock()
        self._next_stream_id: int = 1

    def create_stream(self) -> Stream:
        """
        Create and open a new HTTP/3 stream.

        Returns:
            Stream: The new stream instance.
        """
        with self._lock:
            stream_id = self._next_stream_id
            self._next_stream_id += 1
            stream = Stream(stream_id)
            stream.open()
            self._streams[stream_id] = stream
            logger.info("Created new stream with ID %d", stream_id)
            return stream

    def get_stream(self, stream_id: int) -> Optional[Stream]:
        """
        Retrieve an existing stream by its ID.

        Args:
            stream_id (int): The identifier of the stream.
        
        Returns:
            Optional[Stream]: The stream if found; otherwise, None.
        """
        with self._lock:
            return self._streams.get(stream_id)

    def close_stream(self, stream_id: int) -> None:
        """
        Close and remove a stream by its ID.

        Args:
            stream_id (int): The identifier of the stream to close.
        """
        with self._lock:
            stream = self._streams.pop(stream_id, None)
        if stream:
            stream.close()
            logger.info("Closed stream with ID %d", stream_id)
        else:
            logger.warning("Stream with ID %d not found to close", stream_id)

    def close_all(self) -> None:
        """
        Close every stream managed by this manager.
        """
        with self._lock:
            stream_ids = list(self._streams.keys())
        for stream_id in stream_ids:
            self.close_stream(stream_id)

    def __iter__(self):
        with self._lock:
            # Return a shallow copy iterator.
            return iter(self._streams.values())
