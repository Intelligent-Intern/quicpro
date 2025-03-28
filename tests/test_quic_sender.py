"""
Test module for the QUIC sender.
"""

import unittest
from quicpro.sender.encoder import Encoder, Message
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.exceptions import TransmissionError
from tests.test_utils.dummy_tls_encryptor import DummyTLSEncryptor
from tests.test_utils.dummy_quic_sender import DummyQUICSender
from tests.test_utils.dummy_http3_sender import DummyHTTP3Sender

'''
This test suite is designed to validate the functionality of the QUIC sender module.
It includes tests for the sender pipeline, ensuring that messages are correctly encoded
and sent through the TLS encryptor. Additionally, it tests the handling of sender failures
by raising appropriate exceptions.
'''
class TestSenderPipeline(unittest.TestCase):
    """Test cases for the sender pipeline."""
    def setUp(self):
        self.dummy_encryptor = DummyTLSEncryptor()
        self.dummy_quic_sender = DummyQUICSender(tls_encryptor=self.dummy_encryptor)
        self.dummy_http3_sender = DummyHTTP3Sender(self.dummy_quic_sender, stream_id=9)

    def test_sender_pipeline(self):
        """Test that a message is encoded and correctly sent via the TLS encryptor."""
        encoder = Encoder(http3_sender=self.dummy_http3_sender)
        encoder.encode(Message(content="test"))
        self.assertIsNotNone(self.dummy_encryptor.received_packet,
                             "TLS encryptor did not receive any packet.")
        self.assertIn(b"Frame(test)", self.dummy_encryptor.received_packet,
                      "The encoded frame is missing from the TLS packet.")

    def test_sender_failure(self):
        """Test that a sender failure raises TransmissionError."""
        class FailingSender:
            def send(self, frame: bytes) -> None:
                raise Exception("QUIC Sender failure")
        sender = HTTP3Sender(quic_sender=FailingSender(), stream_id=9)
        with self.assertRaises(TransmissionError):
            sender.send(b"Any frame")

if __name__ == '__main__':
    unittest.main()
