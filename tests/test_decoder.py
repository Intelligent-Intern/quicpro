# pylint: disable=duplicate-code
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
        self.consumer = DummyConsumer()
        self.decoder = Decoder(consumer_app=self.consumer)
    
    """Test that the decoder correctly decodes a valid QUIC packet."""
    def test_decode_valid_frame(self):
        # Provide a QUIC packet containing a valid frame "Frame(Hello World)"
        packet = b"HTTP3:Frame(Hello World)"
        self.decoder.decode(packet)
        self.assertEqual(self.consumer.messages, ["Hello World"])

    """ Test that the decoder raises an error for missing frame data."""
    def test_decode_missing_prefix(self):
        # Provide a packet without the expected "Frame(" pattern
        packet = b"Random Data"
        self.decoder.decode(packet)
        self.assertEqual(self.consumer.messages, ["Unknown"])

if __name__ == '__main__':
    unittest.main()
