"""
DummyQUICSender for testing purposes.
"""

class DummyQUICSender:
    def __init__(self, tls_encryptor):
        self.tls_encryptor = tls_encryptor
        self.sent_frame = None

    def send(self, frame: bytes) -> None:
        """
        Simulate sending a frame via QUIC and forward the packet to the TLS encryptor.
        """
        self.sent_frame = frame
        packet = b"QUICFRAME:dummy:0:1:HTTP3:" + frame
        self.tls_encryptor.encrypt(packet)
