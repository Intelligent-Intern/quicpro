"""
HTTP/3 Stream Manager

This module defines the StreamManager class that manages multiple HTTP/3 streams.
It provides thread-safe methods to create, retrieve, and close streams, assigning
unique IDs to each stream.
"""

import threading
import logging
from typing import Dict, Optional, Iterator

from quicpro.utils.http3.streams.stream import Stream
from quicpro.utils.http3.streams.priority import StreamPriority

logger = logging.getLogger(__name__)


class StreamManager:
    """
    Manages multiple HTTP/3 streams.

    Provides thread-safe methods to create new streams, retrieve existing streams,
    and close streams. Streams are keyed by their unique stream IDs.
    """
    def __init__(self) -> None:
        """
        Initialize a new StreamManager instance.
        """
        self._streams: Dict[int, Stream] = {}
        self._lock = threading.Lock()
        self._next_stream_id: int = 1

    def create_stream(
        self, priority: Optional[StreamPriority] = None
    ) -> Stream:
        """
        Create and open a new HTTP/3 stream.

        Args:
            priority (Optional[StreamPriority]): An optional priority to assign.

        Returns:
            Stream: The newly created and opened stream.
        """
        with self._lock:
            stream_id = self._next_stream_id
            self._next_stream_id += 1
            stream = Stream(stream_id)
            stream.open()
            if priority is not None:
                stream.set_priority(priority)
            self._streams[stream_id] = stream
            logger.info("Created new stream with ID %d", stream_id)
            return stream

    def get_stream(self, stream_id: int) -> Optional[Stream]:
        """
        Retrieve an existing stream by its ID.

        Args:
            stream_id (int): The unique identifier of the stream.

        Returns:
            Optional[Stream]: The stream if found; otherwise, None.
        """
        with self._lock:
            return self._streams.get(stream_id)

    def close_stream(self, stream_id: int) -> None:
        """
        Close and remove a stream by its ID.

        Args:
            stream_id (int): The unique identifier of the stream to close.
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
        Close all streams managed by this manager.
        """
        with self._lock:
            stream_ids = list(self._streams.keys())
        for stream_id in stream_ids:
            self.close_stream(stream_id)

    def __iter__(self) -> Iterator[Stream]:
        """
        Return an iterator over the managed streams.

        Returns:
            Iterator[Stream]: An iterator over the streams.
        """
        with self._lock:
            return iter(self._streams.copy().values())
