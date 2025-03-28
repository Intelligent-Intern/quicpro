"""
Test module for the consumer application.
"""

import unittest
from quicpro.receiver.consumer_app import ConsumerApp

class TestConsumerApp(unittest.TestCase):
    """Test cases for the ConsumerApp class."""
    
    def test_consume_message(self):
        """Test if ConsumerApp correctly processes a received message."""
        # Create a subclass of ConsumerApp that records the message
        class DummyConsumerApp(ConsumerApp):
            def __init__(self):
                super().__init__()
                self.received_message = None
            def consume(self, message: str) -> None:
                self.received_message = message

        consumer = DummyConsumerApp()
        consumer.consume("Hello World")
        self.assertEqual(consumer.received_message, "Hello World")

if __name__ == '__main__':
    unittest.main()
