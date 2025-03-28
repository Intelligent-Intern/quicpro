"""
ProducerApp module.
Accepts a message, creates a Message instance, and passes it to an Encoder.
"""
from typing import Union
from quicpro.sender.encoder import Encoder, Message

class ProducerApp:
    """
    A producer application that creates and sends messages.
    """
    def __init__(self, encoder: Encoder) -> None:
        self.encoder = encoder

    def create_message(self, message: Union[str, Message, dict]) -> None:
        """
        Accept a message (string, dict, or Message) and encode it.
        """
        if isinstance(message, Message):
            msg_obj = message
        elif isinstance(message, dict):
            msg_obj = Message(**message)
        else:
            msg_obj = Message(content=message)
        self.encoder.encode(msg_obj)
