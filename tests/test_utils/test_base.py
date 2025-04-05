# pylint: disable=duplicate-code
"""
Base class for sender tests.
"""
import unittest
from tests.test_utils.dummy_tls_encryptor import DummyTLSEncryptor
from tests.test_utils.dummy_quic_sender import DummyQUICSender
from tests.test_utils.dummy_http3_sender import DummyHTTP3Sender

class BaseSenderTest(unittest.TestCase):
    """Base class for sender tests. It sets up the necessary components for testing."""
    def setUp(self):
        self.dummy_encryptor = DummyTLSEncryptor()
        self.dummy_quic_sender = DummyQUICSender(self.dummy_encryptor)
        self.dummy_http3_sender = DummyHTTP3Sender(self.dummy_quic_sender, stream_id=9)
