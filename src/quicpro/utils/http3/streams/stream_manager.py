"""
HTTP/3 Stream Manager
This module defines the StreamManager class that manages multiple HTTP/3 streams.
It provides methods to create, retrieve, and close streams in a thread-safe manner.
"""
from typing import Optional, Dict, Iterator
from quicpro.utils.http3.streams.stream import Stream
from quicpro.utils.http3.streams.priority import StreamPriority


class StreamManager:
    """Manages multiple HTTP/3 streams."""
    
    def __init__(self) -> None:
        self._streams: Dict[int, Stream] = {}
        self._next_stream_id: int = 1

    def create_stream(self, stream_id: Optional[int] = None, *, priority: Optional[StreamPriority] = None) -> Stream:
        """Creates a new stream or retrieves an existing stream by its ID."""
        if stream_id is None:
            stream_id = self._next_stream_id
            self._next_stream_id += 1
        if stream_id in self._streams:
            stream = self._streams[stream_id]
            if priority is not None:
                stream.set_priority(priority)
            return stream
        stream = Stream(stream_id)
        stream.open()  # Set state to "open"
        if priority is not None:
            stream.set_priority(priority)
        self._streams[stream_id] = stream
        return stream

    def get_stream(self, stream_id: int) -> Optional[Stream]:
        """Retrieves a stream by its ID."""
        return self._streams.get(stream_id)

    def close_stream(self, stream_id: int) -> None:
        """Closes a stream by its ID."""
        stream = self._streams.pop(stream_id, None)
        if stream:
            stream.close()

    def close_all(self) -> None:
        """Closes all streams."""
        for stream in list(self._streams.values()):
            stream.close()
        self._streams.clear()

    def __iter__(self) -> Iterator[Stream]:
        """Returns an iterator over the streams."""
        return iter(self._streams.values())

