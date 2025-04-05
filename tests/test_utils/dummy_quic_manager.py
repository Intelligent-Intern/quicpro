# pylint: disable=duplicate-code
"""
This module contains a dummy QUIC manager for testing purposes.
"""
from tests.test_utils.dummy_connection import DummyConnection

class DummyQuicManager:
    """A dummy QUIC manager that simulates a QUIC connection for testing purposes."""
    def __init__(self):
        self.connection = DummyConnection()
