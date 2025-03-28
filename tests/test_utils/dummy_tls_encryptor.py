"""
DummyTLSEncryptor for testing purposes.
"""

class DummyTLSEncryptor:
    def __init__(self):
        self.received_packet = None

    def encrypt(self, packet: bytes) -> None:
        """Capture the encrypted packet."""
        self.received_packet = packet
