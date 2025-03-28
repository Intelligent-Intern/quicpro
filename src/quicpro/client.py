#!/usr/bin/env python
"""
Production HTTP/3 Client with Integrated Streams, Priority, and QPACK.
Supports both demo and production mode. In demo mode, dummy certificate values are used and
the TLS handshake is simulated so that tests complete in under one second.
"""
import threading
import socket
import time
from typing import Optional, Dict, Any
from urllib.parse import urlsplit, urlunsplit, urlencode
from quicpro.response import Response
from quicpro.utils.quic.quic_manager import QuicManager
from quicpro.utils.http3.connection.http3_connection import HTTP3Connection
from quicpro.utils.tls.tls_manager import TLSManager


class Client:
    """HTTP/3 Client for making requests and handling responses."""
    
    def __init__(self, remote_address: Optional[tuple] = None, timeout: float = 1.0,
                 event_loop_max_workers: int = 2, demo_mode: bool = True,
                 certfile: Optional[str] = None, keyfile: Optional[str] = None,
                 cafile: Optional[str] = None) -> None:
        """Initialize the HTTP/3 Client with necessary parameters."""
        self.remote_address = remote_address or ("127.0.0.1", 9090)
        self.timeout = timeout
        self.quic_manager = QuicManager(
            connection_id="default-conn",
            header_fields={"stream_id": "1"},
            event_loop_max_workers=event_loop_max_workers
        )
        self.http3_connection = HTTP3Connection(self.quic_manager)
        self.demo_mode = demo_mode
        self.tls_manager = self._initialize_tls(certfile, keyfile, cafile)
        self._listener_thread = threading.Thread(
            target=self._listen_for_response, daemon=True)
        self._listener_thread.start()

    def _initialize_tls(self, certfile, keyfile, cafile):
        """Initialize the TLS manager based on the mode."""
        if self.demo_mode:
            return TLSManager("TLSv1.3", certfile="dummy_cert.pem", 
                              keyfile="dummy_key.pem", demo=True)
        else:
            if not (certfile and keyfile):
                raise ValueError(
                    "In production mode, certfile and keyfile must be provided.")
            return TLSManager("TLSv1.3", certfile=certfile, keyfile=keyfile, 
                              cafile=cafile, demo=False)

    def _listen_for_response(self) -> None:
        """Listen for incoming responses from the QUIC connection."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.remote_address)
        sock.settimeout(0.01)
        start_time = time.time()
        try:
            while (time.time() - start_time) < self.timeout:
                try:
                    data, _ = sock.recvfrom(4096)
                    if self.demo_mode:
                        data = self.tls_manager.decrypt_data(data)
                    self.http3_connection.route_incoming_frame(data)
                    break
                except socket.timeout:
                    continue
        finally:
            sock.close()

    def request(self, method: str, url: str, params: Optional[Dict[str, Any]] = None, 
                **kwargs) -> Response:
        """Send a request and return the response."""
        if params:
            url_parts = urlsplit(url)
            query = urlencode(params)
            if url_parts.query:
                query = url_parts.query + "&" + query
            url = urlunsplit((
                url_parts.scheme, url_parts.netloc,
                url_parts.path, query, url_parts.fragment
            ))
        request_body = f"{method} {url}".encode("utf-8")
        request_body = self.tls_manager.encrypt_data(request_body)
        self.http3_connection.send_request(request_body, **kwargs)
        self._listener_thread.join(timeout=2)
        payload = self.http3_connection.receive_response()
        status_code = 200 if payload else 500
        return Response(status_code, payload)

    def close(self) -> None:
        """Close the HTTP/3 connection."""
        self.http3_connection.close()
