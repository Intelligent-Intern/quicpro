"""
Base TLS Handler for common initialization.
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class BaseTLSHandler:
    def __init__(self, config, demo: bool, dtls_context: object = None) -> None:
        self.config = config
        self.demo = demo
        self.dtls_context = dtls_context
        if self.demo:
            self.aesgcm = AESGCM(self.config.key)
        else:
            if self.dtls_context is None:
                raise ValueError("Real TLS mode requires a DTLS/TLS context.")
