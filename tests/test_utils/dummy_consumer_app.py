# pylint: disable=duplicate-code
"""
Dummy consumer app for testing purposes.
"""
from quicpro.receiver.consumer_app import ConsumerApp

class DummyConsumerApp(ConsumerApp):
    """A dummy consumer app that collects messages for testing purposes."""
    def __init__(self):
        super().__init__()
        self.received_message = None
    """Simulate message consumption by storing the message."""
    def consume(self, message: str) -> None:
        self.received_message = message
