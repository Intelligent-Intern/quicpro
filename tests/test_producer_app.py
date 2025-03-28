import unittest
from quicpro.sender.producer_app import ProducerApp
from quicpro.sender.encoder import Message

class DummyEncoder:
    def __init__(self):
        self.encoded_messages = []

    def encode(self, message: Message) -> None:
        # Simply store the content of the message
        self.encoded_messages.append(message.content)

class TestProducerApp(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_encoder = DummyEncoder()
        self.producer_app = ProducerApp(encoder=self.dummy_encoder)

    def test_create_message_with_string(self) -> None:
        # Test with a simple string
        self.producer_app.create_message("Hello World")
        self.assertEqual(self.dummy_encoder.encoded_messages, ["Hello World"],
                         "The message from a string was not correctly passed to the encoder.")

    def test_create_message_with_dict(self) -> None:
        # Test with a dictionary
        self.producer_app.create_message({"content": "Dict Message"})
        self.assertEqual(self.dummy_encoder.encoded_messages, ["Dict Message"],
                         "The message from a dictionary was not correctly passed to the encoder.")

    def test_create_message_with_message_instance(self) -> None:
        # Test with a Message instance
        msg = Message(content="Instance Message")
        self.producer_app.create_message(msg)
        self.assertEqual(self.dummy_encoder.encoded_messages, ["Instance Message"],
                         "The message as a Message instance was not correctly passed to the encoder.")

if __name__ == '__main__':
    unittest.main()
