"""
Test module for sender functionality.
"""

import unittest
from quicpro.sender.encoder import Encoder, Message
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.exceptions import TransmissionError

class DummyTLSEncryptor:
    """A dummy TLS encryptor for testing purposes."""
    def __init__(self):
        self.received_packet = None

    def encrypt(self, packet: bytes) -> None:
        self.received_packet = packet

class DummyQUICSender:
    """A dummy QUIC sender that uses a dummy TLS encryptor."""
    def __init__(self, tls_encryptor: DummyTLSEncryptor):
        self.tls_encryptor = tls_encryptor
        self.sent_frame = None

    def send(self, frame: bytes) -> None:
        self.sent_frame = frame
        packet = b"QUICFRAME:dummy:0:1:HTTP3:" + frame
        self.tls_encryptor.encrypt(packet)

class DummyHTTP3Sender:
    """A dummy HTTP/3 sender wrapping a QUIC sender."""
    def __init__(self, quic_sender: DummyQUICSender, stream_id: int):
        self.quic_sender = quic_sender
        self.stream_id = stream_id

    def send(self, frame: bytes) -> None:
        stream_frame = b"HTTP3Stream(stream_id=%d, payload=Frame(" % self.stream_id + frame + b"))"
        self.quic_sender.send(stream_frame)

class TestSender(unittest.TestCase):
    """Test cases for sender pipeline functionality."""
    def setUp(self):
        self.dummy_encryptor = DummyTLSEncryptor()
        self.dummy_quic_sender = DummyQUICSender(self.dummy_encryptor)
        self.dummy_http3_sender = DummyHTTP3Sender(self.dummy_quic_sender, stream_id=9)

    def test_sender_encode(self):
        """Test that the encoder encodes a message correctly and sends it."""
        encoder = Encoder(http3_sender=self.dummy_http3_sender)
        encoder.encode(Message(content="test"))
        self.assertIsNotNone(self.dummy_encryptor.received_packet,
                             "TLS encryptor did not receive any packet.")
        self.assertIn(b"Frame(test)", self.dummy_encryptor.received_packet,
                      "The encoded frame is missing from the TLS packet.")

if __name__ == '__main__':
    unittest.main()
