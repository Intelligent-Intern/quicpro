# pylint: disable=duplicate-code
import unittest
from quicpro.sender.encoder import Encoder, Message
from quicpro.exceptions.encoding_error import EncodingError
from tests.test_utils.dummy_http3_sender import DummyHTTP3Sender
from tests.test_utils.dummy_quic_sender import DummyQUICSender
from tests.test_utils.dummy_tls_encryptor import DummyTLSEncryptor

class TestEncoder(unittest.TestCase):
    """Test suite for the Encoder class."""
    def setUp(self) -> None:
        dummy_encryptor = DummyTLSEncryptor()
        dummy_quic_sender = DummyQUICSender(dummy_encryptor)
        self.dummy_sender = DummyHTTP3Sender(dummy_quic_sender, stream_id=9)
        self.encoder = Encoder(http3_sender=self.dummy_sender)

    """Test that the Encoder is initialized correctly."""
    def test_initialization(self):
        self.assertIsNotNone(self.encoder, "Encoder should be initialized.")
        self.assertIsNotNone(self.encoder.http3_sender,
                             "HTTP3Sender should be initialized.")
        self.assertIsInstance(self.encoder.http3_sender,
                              DummyHTTP3Sender, "HTTP3Sender should be of the correct type.")

    """Test that the Encoder can encode a valid message."""
    def test_encode_valid_message(self):
        msg = Message(content="Test")
        self.encoder.encode(msg)
        expected_frame = b"Frame(Test)"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")

    """Test that the Encoder can handle an empty message."""
    def test_encode_empty_message(self):
        msg = Message(content="")
        self.encoder.encode(msg)
        expected_frame = b"Frame()"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with special characters."""
    def test_encode_special_characters(self):
        msg = Message(content="!@#$%^&*()")
        self.encoder.encode(msg)
        expected_frame = b"Frame(!@#$%^&*())"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with binary data."""
    def test_encode_binary_data(self):
        msg = Message(content=b"\x00\x01\x02\x03")
        self.encoder.encode(msg)
        expected_frame = b"Frame(b'\\x00\\x01\\x02\\x03')"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a large payload."""
    def test_encode_large_payload(self):
        msg = Message(content="A" * 10000)
        self.encoder.encode(msg)
        expected_frame = b"Frame(" + b"A" * 10000 + b")"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a complex structure."""
    def test_encode_complex_structure(self):
        msg = Message(content={"key1": "value1", "key2": [1, 2, 3]})
        self.encoder.encode(msg)
        expected_frame = b"Frame({'key1': 'value1', 'key2': [1, 2, 3]})"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a None payload."""
    def test_encode_none_payload(self):
        msg = Message(content=None)
        self.encoder.encode(msg)
        expected_frame = b"Frame(None)"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a boolean payload."""
    def test_encode_boolean_payload(self):
        msg = Message(content=True)
        self.encoder.encode(msg)
        expected_frame = b"Frame(True)"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a float payload."""
    def test_encode_float_payload(self):
        msg = Message(content=3.14)
        self.encoder.encode(msg)
        expected_frame = b"Frame(3.14)"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a dictionary payload."""
    def test_encode_dict_payload(self):
        msg = Message(content={"key": "value"})
        self.encoder.encode(msg)
        expected_frame = b"Frame({'key': 'value'})"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
    """Test that the Encoder can handle a message with a list payload."""
    def test_encode_list_payload(self):
        msg = Message(content=["item1", "item2"])
        self.encoder.encode(msg)
        expected_frame = b"Frame(['item1', 'item2'])"
        self.assertEqual(len(self.dummy_sender.sent_frames),
                         1, "Exactly one frame should be sent.")
        self.assertEqual(self.dummy_sender.sent_frames[0], expected_frame,
                         "The produced frame does not match the expected frame.")
        
    """ Test that the Encoder raises an EncodingError on failure. """
    def test_encode_failure(self):
        class FailingSender:
            def send(self, frame: bytes) -> None:
                raise Exception("Sender error")
        encoder = Encoder(http3_sender=FailingSender())
        with self.assertRaises(EncodingError):
            encoder.encode("fail")

if __name__ == '__main__':
    unittest.main()
