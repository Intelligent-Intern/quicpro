"""
Base loop module.
Defines the BaseEventLoop interface.
"""
import abc


class BaseEventLoop(abc.ABC):
    """
    Abstract base class for an event loop.
    """
    @abc.abstractmethod
    def run_forever(self) -> None:
        """Run the event loop indefinitely until stop() is called."""
        ...

    @abc.abstractmethod
    def stop(self) -> None:
        """Stop the event loop."""
        ...

    @abc.abstractmethod
    def schedule_task(self, func, *args, **kwargs):
        """
        Schedule a task to be executed.
        Returns a Future.
        """
        ...
