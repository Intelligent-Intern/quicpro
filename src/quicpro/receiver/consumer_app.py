"""
ConsumerApp module.
Provides a ConsumerApp class to process decoded messages.
"""
import logging
from typing import Optional, Callable
from pydantic import BaseModel, Field
from quicpro.exceptions import PipelineError

logger = logging.getLogger(__name__)


class ConsumerConfig(BaseModel):
    process_callback: Optional[Callable[[str], None]] = Field(default=None)


class ConsumerApp:
    """
    A simple consumer application that processes a received message.
    """

    def __init__(self, config: Optional[ConsumerConfig] = None) -> None:
        """
        Initialize the ConsumerApp with an optional ConsumerConfig.
        """
        if config is None:
            config = ConsumerConfig()
        self.process_callback = config.process_callback

    def consume(self, message: str) -> None:
        """
        Process the received message and invoke the callback.
        """
        try:
            logger.info("ConsumerApp received message: %s", message)
            if self.process_callback:
                self.process_callback(message)
        except Exception as exc:
            logger.exception("ConsumerApp processing failed", exc_info=exc)
            raise PipelineError(f"ConsumerApp failed: {exc}") from exc

