import unittest
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.exceptions import TransmissionError

class DummyQUICSender:
    def __init__(self):
        self.sent_frames = []

    def send(self, frame: bytes) -> None:
        # Simply store the frame for later verification.
        self.sent_frames.append(frame)

class TestHTTP3Sender(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_quic_sender = DummyQUICSender()
        self.stream_id = 9
        self.http3_sender = HTTP3Sender(quic_sender=self.dummy_quic_sender, stream_id=self.stream_id)

    def test_send_valid_frame(self) -> None:
        # Create a sample encoded frame.
        encoded_frame = b"Frame(Test Message)"
        # Call send method.
        self.http3_sender.send(encoded_frame)
        # Expected stream frame is composed as follows:
        # b"HTTP3Stream(stream_id=<stream_id>, payload=" + encoded_frame + b")"
        expected_frame = b"HTTP3Stream(stream_id=%d, payload=" % self.stream_id + encoded_frame + b")"
        self.assertEqual(len(self.dummy_quic_sender.sent_frames), 1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_quic_sender.sent_frames[0], expected_frame,
                         "The produced HTTP3 stream frame does not match the expected frame.")

    def test_send_failure(self) -> None:
        # Simulate a failure in the underlying QUIC sender.
        class FailingQUICSender:
            def send(self, frame: bytes) -> None:
                raise Exception("QUIC Sender failure")

        http3_sender = HTTP3Sender(quic_sender=FailingQUICSender(), stream_id=self.stream_id)
        with self.assertRaises(TransmissionError):
            http3_sender.send(b"Any frame")

if __name__ == '__main__':
    unittest.main()
