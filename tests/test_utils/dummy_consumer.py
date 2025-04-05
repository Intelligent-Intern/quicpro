# pylint: disable=duplicate-code
"""
Dummy consumer for testing purposes.
"""

class DummyConsumer:
    """A dummy consumer that collects messages for testing purposes."""
    def __init__(self):
        self.messages = []

    """Simulate message consumption by appending to a list."""
    def consume(self, message: str) -> None:
        self.messages.append(message)
