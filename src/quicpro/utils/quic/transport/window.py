"""
window.py - Flow control window management for QUIC transport.

Implements a simple flow control window mechanism.
"""


class FlowControlWindow:
    """
    Manages the flow control window for QUIC transport.

    Attributes:
        window_size (int): The maximum number of bytes allowed.
        bytes_consumed (int): The number of bytes already consumed.
    """

    def __init__(self, initial_window: int) -> None:
        """
        Initialize the flow control window.

        Args:
            initial_window (int): The initial window size in bytes.
        """
        self.window_size = initial_window
        self.bytes_consumed = 0

    def consume(self, num_bytes: int) -> None:
        """
        Consume a given number of bytes from the window.

        Args:
            num_bytes (int): The number of bytes to consume.

        Raises:
            ValueError: If consumption exceeds the window size.
        """
        if self.bytes_consumed + num_bytes > self.window_size:
            raise ValueError("Flow control window exceeded")
        self.bytes_consumed += num_bytes

    def update_window(self, new_window: int) -> None:
        """
        Update the flow control window and reset the consumed bytes.

        Args:
            new_window (int): The new window size in bytes.
        """
        self.window_size = new_window
        self.bytes_consumed = 0

    def available(self) -> int:
        """
        Return the number of bytes available in the window.

        Returns:
            int: The available window size.
        """
        return self.window_size - self.bytes_consumed
