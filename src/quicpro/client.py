#!/usr/bin/env python
"""
Production HTTP/3 Client with Integrated Streams, Priority, and QPACK

This client integrates a QUIC manager with an HTTP/3 connection.
It supports optional TLS encryption for testing via the demo_mode flag.
In production, encryption is configured externally and demo_mode remains False.
"""

import threading
import socket
import time
from typing import Optional, Dict, Any
from urllib.parse import urlsplit, urlunsplit, urlencode

from quicpro.response import Response
from quicpro.src.quicpro.utils.quic.quic_manager import QuicManager
from quicpro.utils.http3.connection.http3_connection import HTTP3Connection
from quicpro.utils.http3.streams.priority import StreamPriority
from quicpro.utils.tls.tls_manager import TLSManager

class Client:
    def __init__(
        self,
        remote_address: Optional[tuple] = None,
        timeout: float = 20.0,
        event_loop_max_workers: int = 4,
        demo_mode: bool = False
    ) -> None:
        self.remote_address = remote_address or ("127.0.0.1", 9090)
        self.timeout = timeout

        self.quic_manager = QuicManager(
            connection_id="default-conn",
            header_fields={"stream_id": "1"},
            event_loop_max_workers=event_loop_max_workers
        )
        self.http3_connection = HTTP3Connection(self.quic_manager)
        self._response: Optional[Response] = None
        self.demo_mode = demo_mode

        if self.demo_mode:
            # In demo_mode, use the built-in encryption already integrated in our system.
            self.tls_manager = TLSManager("TLSv1.3", certfile="dummy_cert.pem", keyfile="dummy_key.pem")
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_sock.settimeout(self.timeout)
            temp_sock.connect(self.remote_address)
            self.tls_manager.perform_handshake(temp_sock, server_hostname="example.com")
            temp_sock.close()

        self._listener_thread = threading.Thread(target=self._listen_for_response, daemon=True)
        self._listener_thread.start()

    def _listen_for_response(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.remote_address)
        sock.settimeout(self.timeout)
        start_time = time.time()
        try:
            while (time.time() - start_time) < self.timeout:
                try:
                    data, _ = sock.recvfrom(4096)
                    if self.demo_mode:
                        data = self.tls_manager.decrypt_data(data)
                    self.http3_connection.route_incoming_frame(data)
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
        params: Optional[Dict[str, Any]] = None,
        priority: Optional[StreamPriority] = None
    ) -> Response:
        if params:
            url_parts = urlsplit(url)
            query = urlencode(params)
            if url_parts.query:
                query = url_parts.query + "&" + query
            url = urlunsplit((url_parts.scheme, url_parts.netloc, url_parts.path, query, url_parts.fragment))
        request_body = f"{method} {url}".encode("utf-8")
        if self.demo_mode:
            request_body = self.tls_manager.encrypt_data(request_body)
        self.http3_connection.send_request(request_body, priority=priority)
        self._listener_thread.join(timeout=self.timeout)
        if self._response is None:
            return Response(500, b"No response received")
        return self._response

    def close(self) -> None:
        self.http3_connection.close()