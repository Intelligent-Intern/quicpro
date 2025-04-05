"""
Test module for sender functionality.
"""
import unittest
from quicpro.sender.encoder import Encoder, Message
from tests.test_utils.test_base import BaseSenderTest

class TestSender(BaseSenderTest):
    def test_sender_encode(self):
        encoder = Encoder(http3_sender=self.dummy_http3_sender)
        encoder.encode(Message(content="test"))
        self.assertIsNotNone(
            self.dummy_encryptor.received_packet,
            "TLS encryptor did not receive any packet."
        )
        self.assertIn(
            b"Frame(test)",
            self.dummy_encryptor.received_packet,
            "The encoded frame is missing from the TLS packet."
        )

if __name__ == '__main__':
    unittest.main()
