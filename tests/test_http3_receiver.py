import unittest
from quicpro.receiver.http3_receiver import HTTP3Receiver
from quicpro.exceptions.http3_frame_error import HTTP3FrameError

class DummyConsumerApp:
    def __init__(self):
        self.received_message = None

    def consume(self, message: str) -> None:
        self.received_message = message

class DummyDecoder:
    def __init__(self, consumer_app):
        self.consumer_app = consumer_app

    def decode(self, frame: bytes) -> None:
        # If frame starts with "Frame(" and ends with ")", extract inner content.
        if frame.startswith(b"Frame(") and frame.endswith(b")"):
            self.consumer_app.consume(frame[len(b"Frame("):-1].decode("utf-8"))
        else:
            self.consumer_app.consume(frame.decode("utf-8"))

    def consume(self, message: str) -> None:
        self.consumer_app.consume(message)

class TestReceiverPipeline(unittest.TestCase):
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

    def test_receiver_invalid_frame(self):
        with self.assertRaises(HTTP3FrameError):
            http3_receiver = HTTP3Receiver(decoder=DummyDecoder(None))
            http3_receiver.receive(b"")

if __name__ == '__main__':
    unittest.main()