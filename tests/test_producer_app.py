"""
Test suite for ProducerApp functionality.
"""
import unittest
from quicpro.sender.producer_app import ProducerApp
from quicpro.sender.encoder import Message
from tests.test_utils.dummy_encoder import DummyEncoder

class TestProducerApp(unittest.TestCase):
    """Test cases for the ProducerApp module."""
    
    def setUp(self) -> None:
        self.dummy_encoder = DummyEncoder()
        self.producer_app = ProducerApp(encoder=self.dummy_encoder)
    
    def test_create_message_with_string(self) -> None:
        self.producer_app.create_message("Hello World")
        self.assertEqual(
            self.dummy_encoder.encoded_messages,
            ["Hello World"],
            "Message from a string was not correctly passed to the encoder."
        )
    
    def test_create_message_with_dict(self) -> None:
        self.producer_app.create_message({"content": "Dict Message"})
        self.assertEqual(
            self.dummy_encoder.encoded_messages,
            ["Dict Message"],
            "Message from a dictionary was not correctly passed to the encoder."
        )
    
    def test_create_message_with_message_instance(self) -> None:
        msg = Message(content="Instance Message")
        self.producer_app.create_message(msg)
        self.assertEqual(
            self.dummy_encoder.encoded_messages,
            ["Instance Message"],
            "Message instance was not correctly passed to the encoder."
        )

if __name__ == "__main__":
    unittest.main()
