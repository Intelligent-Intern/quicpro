'''
Dummy encoder for testing purposes.'
'''

from quicpro.sender.encoder import Message

class DummyEncoder:
    """Dummy encoder for testing ProducerApp."""
    
    def __init__(self):
        self.encoded_messages = []
    
    def encode(self, message: Message) -> None:
        """Simulate encoding by capturing the message content."""
        self.encoded_messages.append(message.content)
