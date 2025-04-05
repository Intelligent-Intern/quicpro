"""
TLSv1.2 Context Implementation

This class configures an SSLContext specifically for TLSv1.2, loads the necessary certificates,
and provides a method to wrap sockets.
"""

import ssl
from typing import Optional
import socket

class TLS12Context:
    def __init__(self, certfile: str, keyfile: str, cafile: Optional[str] = None) -> None:
        """
        Initialize a TLSv1.2 context.

        :param certfile: Path to the certificate file (PEM).
        :param keyfile: Path to the private key file (PEM).
        :param cafile: Optional path to the CA bundle.
        """
        self.certfile = certfile
        self.keyfile = keyfile
        self.cafile = cafile
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.context.maximum_version = ssl.TLSVersion.TLSv1_2
        self.context.load_cert_chain(certfile, keyfile)
        if cafile:
            self.context.verify_mode = ssl.CERT_REQUIRED
            self.context.check_hostname = True
        else:
            self.context.verify_mode = ssl.CERT_NONE
            self.context.check_hostname = False

    def wrap_socket(self, sock: socket.socket, server_hostname: str) -> ssl.SSLSocket:
        """
        Wrap the provided socket with the configured TLSv1.2 context.

        :param sock: The socket to wrap.
        :param server_hostname: The server hostname for SNI.
        :return: A wrapped SSL socket.
        """
        return self.context.wrap_socket(sock, server_hostname=server_hostname)

    def update_keys(self) -> None:
        """
        Stub method for key updates in TLSv1.2 context.
        """
        pass
