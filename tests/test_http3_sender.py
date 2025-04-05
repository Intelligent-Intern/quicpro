"""
Test module for the HTTP3 sender.
"""
import unittest
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.exceptions import TransmissionError
from quicpro.sender.encoder import Encoder, Message
from tests.test_utils.test_base import BaseSenderTest

class TestHTTP3Sender(BaseSenderTest):
    def test_sender_pipeline(self):
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

    def test_sender_failure(self):
        class FailingSender:
            def send(self, frame: bytes) -> None:
                raise Exception("QUIC Sender failure")

        sender = HTTP3Sender(quic_sender=FailingSender(), stream_id=9)
        with self.assertRaises(TransmissionError):
            sender.send(b"Any frame")

if __name__ == '__main__':
    unittest.main()
