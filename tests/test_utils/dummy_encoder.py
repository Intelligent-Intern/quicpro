# pylint: disable=duplicate-code
"""
Dummy encoder for testing purposes.'
"""
from quicpro.sender.encoder import Message

class DummyEncoder:
    """A dummy encoder that simulates encoding messages for testing purposes."""    
    def __init__(self):
        self.encoded_messages = []
    
    """Simulate encoding by appending the message content to a list."""
    def encode(self, message: Message) -> None:
        self.encoded_messages.append(message.content)
