from pydantic import BaseModel

"""
This module defines the Message model that encapsulates the content to be transmitted.
"""

class Message(BaseModel):
    """
    Message model that encapsulates the content to be transmitted.
    """
    content: str

