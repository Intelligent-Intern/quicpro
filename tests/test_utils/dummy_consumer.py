'''
Dummy consumer for testing purposes.
'''
class DummyConsumer:
    """A dummy consumer that collects messages for testing purposes."""
    # pylint: disable=R0903
    def __init__(self):
        self.messages = []

    def consume(self, message: str) -> None:
        """Collect a message from the decoder."""
        self.messages.append(message)
