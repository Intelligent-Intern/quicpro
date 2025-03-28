"""
Module quicpro.response
This module provides an HTTP Response class along with related helper methods to
work with HTTP responses in a chunked and incremental manner.
"""
import codecs
from typing import Iterator, Optional, Dict


class HTTPStatusError(Exception):
    """
    Exception raised when an HTTP response has an error status.
    """
    pass


class Response:
    """
    A Response class to represent an HTTP response.

    Attributes:
        status_code (int): The HTTP status code of the response.
        _content (bytes): The raw response content stored as bytes.
        headers (Dict[str, str]): Optional dictionary of HTTP headers.
    """
    def __init__(self, status_code: int, content: bytes, 
                 headers: Optional[Dict[str, str]] = None) -> None:
        """
        Initialize a new Response instance.

        Args:
            status_code (int): HTTP status code.
            content (bytes or str): Raw response content. If a str is provided,
                it is encoded as UTF-8.
            headers (Optional[Dict[str, str]]): HTTP response headers.
        """
        self.status_code = status_code
        if isinstance(content, bytes):
            self._content = content
        else:
            self._content = content.encode("utf-8")
        self.headers = headers or {}

    @property
    def content(self) -> str:
        """
        Return the fully decoded content as a string.
        """
        return self._content.decode("utf-8", errors="replace")

    @property
    def text(self) -> str:
        """
        Alias for content – return the fully decoded string.
        """
        return self.content

    def iter_bytes(self, chunk_size: int = 1024) -> Iterator[bytes]:
        """
        Yield raw bytes in chunks.

        Args:
            chunk_size (int): Size in bytes.
        """
        yield from (
            self._content[i : i + chunk_size]
            for i in range(0, len(self._content), chunk_size)
        )

    def iter_text(self, encoding: str = "utf-8", errors: str = "strict",
                  chunk_size: int = 1024) -> Iterator[str]:
        """
        Incrementally decode and yield text.

        Args:
            encoding (str): Text encoding.
            errors (str): How to handle errors.
            chunk_size (int): Chunk size in bytes.
        """
        decoder = codecs.getincrementaldecoder(encoding)(errors=errors)
        for byte_chunk in self.iter_bytes(chunk_size):
            text_chunk = decoder.decode(byte_chunk)
            if text_chunk:
                yield text_chunk
        final_chunk = decoder.decode(b'', final=True)
        if final_chunk:
            yield final_chunk

    def iter_lines(self) -> Iterator[str]:
        """
        Yield lines from the full decoded text.
        """
        yield from self.text.splitlines()

    def raise_for_status(self) -> None:
        """
        Raise an HTTPStatusError if the response indicates an error.
        """
        if not 200 <= self.status_code < 400:
            raise HTTPStatusError(f"HTTP error: {self.status_code}")

    def __repr__(self) -> str:
        """
        Return a string representation for debugging.
        """
        summary = (
            self.text[:100].replace("\n", " ")
            if self.text
            else "Empty"
        )
        return f"<Response {self.status_code}: {summary}>"
"""
Module quicpro.response
This module provides an HTTP Response class along with related helper methods to
work with HTTP responses in a chunked and incremental manner.
"""
import codecs
from typing import Iterator, Optional, Dict


class HTTPStatusError(Exception):
    """
    Exception raised when an HTTP response has an error status.
    """
    pass


class Response:
    """
    A Response class to represent an HTTP response.

    Attributes:
        status_code (int): The HTTP status code of the response.
        _content (bytes): The raw response content stored as bytes.
        headers (Dict[str, str]): Optional dictionary of HTTP headers.
    """
    def __init__(self, status_code: int, content: bytes, 
                 headers: Optional[Dict[str, str]] = None) -> None:
        """
        Initialize a new Response instance.

        Args:
            status_code (int): HTTP status code.
            content (bytes or str): Raw response content. If a str is provided,
                it is encoded as UTF-8.
            headers (Optional[Dict[str, str]]): HTTP response headers.
        """
        self.status_code = status_code
        if isinstance(content, bytes):
            self._content = content
        else:
            self._content = content.encode("utf-8")
        self.headers = headers or {}

    @property
    def content(self) -> str:
        """
        Return the fully decoded content as a string.
        """
        return self._content.decode("utf-8", errors="replace")

    @property
    def text(self) -> str:
        """
        Alias for content – return the fully decoded string.
        """
        return self.content

    def iter_bytes(self, chunk_size: int = 1024) -> Iterator[bytes]:
        """
        Yield raw bytes in chunks.

        Args:
            chunk_size (int): Size in bytes.
        """
        yield from (
            self._content[i : i + chunk_size]
            for i in range(0, len(self._content), chunk_size)
        )

    def iter_text(self, encoding: str = "utf-8", errors: str = "strict",
                  chunk_size: int = 1024) -> Iterator[str]:
        """
        Incrementally decode and yield text.

        Args:
            encoding (str): Text encoding.
            errors (str): How to handle errors.
            chunk_size (int): Chunk size in bytes.
        """
        decoder = codecs.getincrementaldecoder(encoding)(errors=errors)
        for byte_chunk in self.iter_bytes(chunk_size):
            text_chunk = decoder.decode(byte_chunk)
            if text_chunk:
                yield text_chunk
        final_chunk = decoder.decode(b'', final=True)
        if final_chunk:
            yield final_chunk

    def iter_lines(self) -> Iterator[str]:
        """
        Yield lines from the full decoded text.
        """
        yield from self.text.splitlines()

    def raise_for_status(self) -> None:
        """
        Raise an HTTPStatusError if the response indicates an error.
        """
        if not 200 <= self.status_code < 400:
            raise HTTPStatusError(f"HTTP error: {self.status_code}")

    def __repr__(self) -> str:
        """
        Return a string representation for debugging.
        """
        summary = (
            self.text[:100].replace("\n", " ")
            if self.text
            else "Empty"
        )
        return f"<Response {self.status_code}: {summary}>"
