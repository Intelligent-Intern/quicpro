"""
Test module for UDPSender functionality.
"""

import unittest
import time
from quicpro.sender.udp_sender import UDPSender
from quicpro.exceptions import TransmissionError

class DummyNetwork:
    """A dummy network that always succeeds in transmitting packets."""
    def __init__(self, bytes_to_send=10):
        self.bytes_to_send = bytes_to_send
        self.attempts = 0
        self.closed = False
    def transmit(self, packet: bytes) -> int:
        self.attempts += 1
        return self.bytes_to_send
    def close(self):
        self.closed = True

class FailingNetwork:
    """A network that always fails to transmit packets."""
    def __init__(self):
        self.attempts = 0
    def transmit(self, packet: bytes) -> int:
        self.attempts += 1
        raise Exception("Transmission failed")

class FlakyNetwork:
    """A network that fails a given number of times before succeeding."""
    def __init__(self, fail_times=1, bytes_to_send=10):
        self.fail_times = fail_times
        self.bytes_to_send = bytes_to_send
        self.attempts = 0
    def transmit(self, packet: bytes) -> int:
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise Exception("Simulated failure")
        return self.bytes_to_send

class TestUDPSender(unittest.TestCase):
    """Test cases for the UDPSender."""
    def test_successful_send(self):
        """Test that UDPSender sends the packet successfully on the first attempt."""
        network = DummyNetwork(bytes_to_send=20)
        sender = UDPSender(network=network, max_retries=3, retry_delay=0.1)
        bytes_sent = sender.send(b"dummy packet")
        self.assertEqual(bytes_sent, 20)
        self.assertEqual(network.attempts, 1)

    def test_retry_and_success(self):
        """Test that UDPSender retries and then succeeds when initial attempts fail."""
        network = FlakyNetwork(fail_times=2, bytes_to_send=15)
        sender = UDPSender(network=network, max_retries=3, retry_delay=0.1)
        bytes_sent = sender.send(b"dummy packet")
        self.assertEqual(bytes_sent, 15)
        self.assertEqual(network.attempts, 3)

    def test_retry_failure(self):
        """Test that UDPSender raises TransmissionError if all retry attempts fail."""
        network = FailingNetwork()
        sender = UDPSender(network=network, max_retries=2, retry_delay=0.1)
        with self.assertRaises(TransmissionError):
            sender.send(b"dummy packet")
        self.assertEqual(network.attempts, 3)

    def test_context_manager(self):
        """Test that UDPSender context manager calls network.close() upon exit."""
        network = DummyNetwork()
        sender = UDPSender(network=network)
        with sender as s:
            self.assertIs(s, sender, "The __enter__ method should return the sender instance.")
        self.assertTrue(network.closed, "The network's close() method should have been called.")

if __name__ == '__main__':
    unittest.main()
