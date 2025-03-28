import unittest
from quicpro.receiver.decoder import Decoder
from quicpro.exceptions import DecodingError

# Dummy consumer to capture messages produced by the Decoder.
class DummyConsumer:
    def __init__(self):
        self.messages = []
    def consume(self, message: str) -> None:
        self.messages.append(message)

class TestDecoder(unittest.TestCase):
    def setUp(self):
        self.consumer = DummyConsumer()
        self.decoder = Decoder(consumer_app=self.consumer)
    
    def test_decode_valid_frame(self):
        # Provide a QUIC packet that contains a valid frame: "Frame(Hello World)"
        packet = b"HTTP3:Frame(Hello World)"
        self.decoder.decode(packet)
        # The decoder should extract "Hello World" from the packet.
        self.assertEqual(self.consumer.messages, ["Hello World"])
    
    def test_decode_missing_prefix(self):
        # Provide a packet without the expected "Frame(" pattern.
        packet = b"Random Data"
        self.decoder.decode(packet)
        # In this case, the decoder should default to "Unknown".
        self.assertEqual(self.consumer.messages, ["Unknown"])

if __name__ == '__main__':
    unittest.main()
