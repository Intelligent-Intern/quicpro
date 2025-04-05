# pylint: disable=duplicate-code
"""
DummyTLSEncryptor for testing purposes.
"""

class DummyTLSEncryptor:
    """A dummy TLS encryptor that captures encrypted packets for testing purposes."""
    def __init__(self):
        self.received_packet = None

    """Simulate encryption by capturing the packet."""
    def encrypt(self, packet: bytes) -> None:
        self.received_packet = packet
