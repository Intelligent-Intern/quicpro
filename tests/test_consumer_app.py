# pylint: disable=duplicate-code
"""
Test module for the consumer application.
"""
import unittest
from quicpro.receiver.consumer_app import ConsumerApp
from tests.test_utils.dummy_consumer_app import DummyConsumerApp

class TestConsumerApp(unittest.TestCase):
    """Test cases for the ConsumerApp class."""
    def test_consume_message(self):
        """Test if ConsumerApp correctly processes a received message."""
        consumer = DummyConsumerApp()
        consumer.consume("Hello World")
        self.assertEqual(consumer.received_message, "Hello World")

if __name__ == '__main__':
    unittest.main()
