#!/usr/bin/env python
"""
Client module for handling full QUIC communication via the integrated QuicManager.
This module defines the Client class that:
  - Uses QuicManager for managing connection, header, stream, and packet operations.
  - Sends requests formatted as QUIC stream frames.
  - Listens for UDP responses and processes them via the QuicManager.
  - Returns a Response once a simulated QUIC response is received.
"""

import threading
import socket
import time
from typing import Optional, Dict, Any
from urllib.parse import urlsplit, urlunsplit, urlencode

from quicpro.utils.quic.manager import QuicManager
from quicpro.response import Response


class Client:
    """
    Client that handles full QUIC communication using the integrated QuicManager.
    Parameters:
      connection_id (str): Unique identifier for the connection.
      remote_address (tuple, optional): Remote address to bind to.
      timeout (float): Timeout for network operations in seconds.
      event_loop_max_workers (int): Maximum number of workers for the custom event loop.
    Note:
      The parameters `headers`, `json_body`, and `data` in request() are currently unused and are reserved for future enhancements.
    """
    def __init__(
        self,
        connection_id: str = "default-conn",
        remote_address: Optional[tuple] = None,
        timeout: float = 20.0,
        event_loop_max_workers: int = 4
    ) -> None:
        self.remote_address = remote_address or ("127.0.0.1", 9090)
        self.timeout = timeout
        # Pass configurable max_workers to the underlying QuicManager.
        self.quic_manager = QuicManager(
            connection_id,
            header_fields={"stream_id": "1"},
            event_loop_max_workers=event_loop_max_workers
        )
        self._response: Optional[Response] = None
        self._receiver_thread = threading.Thread(
            target=self._listen_for_response, daemon=True
        )
        self._receiver_thread.start()

    def _listen_for_response(self) -> None:
        """Listen for UDP responses and let QuicManager process them."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.remote_address)
        sock.settimeout(self.timeout)
        start_time = time.time()
        try:
            while (time.time() - start_time) < self.timeout:
                try:
                    data, _ = sock.recvfrom(4096)
                    # Let the QuicManager process the received packet.
                    self.quic_manager.receive_packet(data)
                    # For simulation purposes, assume the QuicManager produces a response.
                    self._response = Response(200, b"Simulated response")
                    break
                except socket.timeout:
                    continue
        finally:
            sock.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,  # Reserved for future use.
        json_body: Optional[Dict[Any, Any]] = None,  # Reserved for future use.
        data: Optional[Any] = None  # Reserved for future use.
    ) -> Response:
        """
        Make a QUIC request.
        Parameters:
          method (str): HTTP method.
          url (str): Request URL.
          params (dict, optional): Query parameters to append to the URL.
          headers (dict, optional): Reserved.
          json_body (dict, optional): Reserved.
          data (any, optional): Reserved.
        Returns:
          Response: The response produced by the QUIC pipeline.
        """
        if params:
            url_parts = urlsplit(url)
            query = urlencode(params)
            if url_parts.query:
                query = url_parts.query + "&" + query
            url = urlunsplit((
                url_parts.scheme,
                url_parts.netloc,
                url_parts.path,
                query,
                url_parts.fragment
            ))
        request_message = f"{method} {url}"
        # Use QuicManager to send a stream frame encapsulating the request.
        self.quic_manager.send_stream(stream_id=1, stream_frame=request_message.encode("utf-8"))
        self._receiver_thread.join(timeout=self.timeout)
        if self._response is None:
            return Response(500, b"No response received")
        return self._response

    def close(self) -> None:
        """Close the client by closing the underlying QuicManager components."""
        self.quic_manager.close()
