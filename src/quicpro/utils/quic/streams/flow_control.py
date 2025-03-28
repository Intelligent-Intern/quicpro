"""
flow_control.py - Per-stream flow control for QUIC streams.

This module provides a class to manage the flow control window for an individual
QUIC stream, tracking the available credit for sending data.
"""


class StreamFlowControl:
    """
    Manages the flow control window for a QUIC stream.

    Attributes:
        window_size (int): Total credit available for sending data.
        bytes_sent (int): The amount of data already sent.
    """

    def __init__(self, initial_window: int) -> None:
        """
        Initialize the flow control window.

        Args:
            initial_window (int): The initial window size in bytes.
        """
        self.window_size = initial_window
        self.bytes_sent = 0

    def can_send(self, data_length: int) -> bool:
        """
        Check if the specified amount of data can be sent without exceeding the window.

        Args:
            data_length (int): The length of data to be sent.

        Returns:
            bool: True if data can be sent; otherwise, False.
        """
        return (self.bytes_sent + data_length) <= self.window_size

    def record_send(self, data_length: int) -> None:
        """
        Record the sending of data.

        Args:
            data_length (int): The length of the data sent.

        Raises:
            ValueError: If adding the data_length exceeds the window size.
        """
        if not self.can_send(data_length):
            raise ValueError("Flow control window exceeded for this stream.")
        self.bytes_sent += data_length

    def update_window(self, new_window: int) -> None:
        """
        Update the flow control window and reset the sent data counter.

        Args:
            new_window (int): The new window size in bytes.
        """
        self.window_size = new_window
        self.bytes_sent = 0
