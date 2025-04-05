# pylint: disable=duplicate-code
"""
DummyConnection is a mock class that simulates a network connection for testing purposes.
"""

class DummyConnection:
    """A dummy connection that simulates a network connection for testing purposes."""
    def __init__(self):
        self.sent_packets = []
        self.is_open = True

    """Simulate receiving a packet by appending it to the sent_packets list."""
    def send_packet(self, packet: bytes) -> None:
        self.sent_packets.append(packet)

    """Simulate receiving a packet by returning the first packet in the sent_packets list."""
    def receive_packet(self) -> bytes:
        if self.sent_packets:
            return self.sent_packets.pop(0)
        return None

    """Check if the connection is open."""
    def is_open(self) -> bool:
        return self.is_open

    """Simulate closing the connection."""
    def close(self):
        self.is_open = False
