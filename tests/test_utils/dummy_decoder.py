# pylint: disable=duplicate-code
"""
Dummy decoder for testing purposes.
"""

class DummyDecoder:
    """Dummy decoder for testing purposes."""
    def __init__(self, consumer_app):
        self.consumer_app = consumer_app

    """Simulate decoding by capturing the frame content."""  
    def decode(self, frame: bytes) -> None:
        if frame.startswith(b"Frame(") and frame.endswith(b")"):
            self.consumer_app.consume(frame[len(b"Frame("):-1].decode("utf-8"))
        else:
            self.consumer_app.consume(frame.decode("utf-8"))

    """ Simulate message consumption by appending to a list. """
    def consume(self, message: str) -> None:
        self.consumer_app.consume(message)
