"""
Test module for the Decoder.
"""

import unittest
from quicpro.receiver.decoder import Decoder
from quicpro.exceptions import DecodingError
from tests.test_utils.dummy_consumer import DummyConsumer

class TestDecoder(unittest.TestCase):
    """Test suite for the Decoder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.consumer = DummyConsumer()
        self.decoder = Decoder(consumer_app=self.consumer)
    
    def test_decode_valid_frame(self):
        """Test that a valid frame is correctly decoded."""
        # Provide a QUIC packet containing a valid frame "Frame(Hello World)"
        packet = b"HTTP3:Frame(Hello World)"
        self.decoder.decode(packet)
        self.assertEqual(self.consumer.messages, ["Hello World"])
    
    def test_decode_missing_prefix(self):
        """Test that an invalid packet is handled as unknown."""
        # Provide a packet without the expected "Frame(" pattern
        packet = b"Random Data"
        self.decoder.decode(packet)
        self.assertEqual(self.consumer.messages, ["Unknown"])

if __name__ == '__main__':
    unittest.main()
