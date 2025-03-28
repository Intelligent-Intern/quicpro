import unittest
from quicpro.receiver.http3_receiver import HTTP3Receiver
from quicpro.exceptions.http3_frame_error import HTTP3FrameError


class DummyConsumerApp:
    def __init__(self):
        self.received_message = None

    def consume(self, message: str) -> None:
        self.received_message = message


class TestReceiverPipeline(unittest.TestCase):
    def test_receiver_pipeline(self):
        dummy_consumer = DummyConsumerApp()
        from quicpro.receiver.decoder import Decoder
        decoder = Decoder(consumer_app=dummy_consumer)
        header_block = b"TestHeader"
        length_prefix = len(header_block).to_bytes(2, "big")
        frame = length_prefix + header_block
        http3_receiver = HTTP3Receiver(decoder=decoder)
        http3_receiver._decode_frame = lambda f: (header_block, b"")
        try:
            http3_receiver.receive(frame)
        except Exception as e:
            self.fail(f"HTTP3Receiver raised an unexpected error: {e}")

    def test_receiver_invalid_frame(self):
        with self.assertRaises(HTTP3FrameError):
            http3_receiver = HTTP3Receiver(decoder=None)
            http3_receiver.receive(b"")


if __name__ == '__main__':
    unittest.main()
