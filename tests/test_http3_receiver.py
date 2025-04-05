# pylint: disable=duplicate-code
"""
Test module for the HTTP3Receiver.
"""

import unittest
from quicpro.receiver.http3_receiver import HTTP3Receiver
from quicpro.exceptions.http3_frame_error import HTTP3FrameError
from tests.test_utils.dummy_consumer_app import DummyConsumerApp
from tests.test_utils.dummy_decoder import DummyDecoder

class TestReceiverPipeline(unittest.TestCase):
    """Test cases for the HTTP3Receiver class."""
    def test_receiver_pipeline(self):
        dummy_consumer = DummyConsumerApp()
        decoder = DummyDecoder(dummy_consumer)
        header_block = b"TestHeader"
        length_prefix = len(header_block).to_bytes(2, "big")
        frame = length_prefix + header_block
        http3_receiver = HTTP3Receiver(decoder=decoder)
        try:
            http3_receiver.receive(frame)
        except Exception as e:
            self.fail(f"HTTP3Receiver raised an unexpected error: {e}")
        self.assertEqual(dummy_consumer.received_message, "TestHeader")

    """Test that an invalid frame raises an HTTP3FrameError."""
    def test_receiver_invalid_frame(self):
        with self.assertRaises(HTTP3FrameError):
            http3_receiver = HTTP3Receiver(decoder=DummyDecoder(None))
            http3_receiver.receive(b"")

if __name__ == '__main__':
    unittest.main()
