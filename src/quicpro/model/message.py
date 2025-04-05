"""
This module defines the Message model that encapsulates the content to be transmitted.
"""
from pydantic import BaseModel
from typing import Any

class Message(BaseModel):
    """
    Message model that encapsulates the content to be transmitted.
    """
    content: Any
