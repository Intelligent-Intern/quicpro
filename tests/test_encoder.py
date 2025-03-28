import unittest
from quicpro.sender.encoder import Encoder, Message
from quicpro.exceptions.encoding_error import EncodingError


class DummyHTTP3Sender:
    def __init__(self):
        self.sent_frames = []

    def send(self, frame: bytes) -> None:
        self.sent_frames.append(frame)


class TestEncoder(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_sender = DummyHTTP3Sender()
        self.encoder = Encoder(http3_sender=self.dummy_sender)

    def test_encode_valid_message(self):
        msg = Message(content="Test")
        self.encoder.encode(msg)
        expected_frame = b"Frame(Test)"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")

    def test_encode_failure(self):
        class FailingSender:
            def send(self, frame: bytes) -> None:
                raise Exception("Sender error")
        encoder = Encoder(http3_sender=FailingSender())
        with self.assertRaises(EncodingError):
            encoder.encode("fail")


if __name__ == '__main__':
    unittest.main()
