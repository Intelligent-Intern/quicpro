import unittest
from quicpro.receiver.consumer_app import ConsumerApp

class TestConsumerApp(unittest.TestCase):
    def test_consume_message(self):
        # Create a subclass of ConsumerApp to capture the consumed message.
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
