import unittest
from quicpro.receiver.http3_receiver import HTTP3Receiver
from quicpro.exceptions import HTTP3FrameError

# Dummy decoder to capture frames passed by HTTP3Receiver.
class DummyDecoder:
    def __init__(self):
        self.received_frame = None
    def decode(self, frame: bytes) -> None:
        self.received_frame = frame

class TestHTTP3Receiver(unittest.TestCase):
    def setUp(self):
        self.dummy_decoder = DummyDecoder()
        self.http3_receiver = HTTP3Receiver(decoder=self.dummy_decoder)
    
    def test_receive_valid_http3_frame(self):
        # Provide a packet containing a proper HTTP3 frame.
        # The expected format for extraction is that the payload starts with "HTTP3:" and ends with "\n".
        packet = b"HTTP3:Frame(Hello World)\n"
        self.http3_receiver.receive(packet)
        # The _extract_http3_frame method strips "HTTP3:" and the newline.
        # Therefore, the dummy decoder should have received b"Frame(Hello World)".
        self.assertEqual(self.dummy_decoder.received_frame, b"Frame(Hello World)")

if __name__ == '__main__':
    unittest.main()
