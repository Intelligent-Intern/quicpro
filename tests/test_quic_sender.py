import unittest
import hashlib
from quicpro.sender.quic_sender import QUICSender
from quicpro.exceptions import TransmissionError

class DummyTLSEncryptor:
    def __init__(self):
        self.encrypted_packets = []

    def encrypt(self, packet: bytes) -> None:
        # Simply store the encrypted packet for later verification.
        self.encrypted_packets.append(packet)

class TestQUICSender(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_encryptor = DummyTLSEncryptor()
        self.quic_sender = QUICSender(tls_encryptor=self.dummy_encryptor)

    def test_send_valid_stream_frame(self) -> None:
        # Sample HTTP/3 stream frame
        stream_frame = b"HTTP3Stream(stream_id=9, payload=Frame(Test))"
        self.quic_sender.send(stream_frame)
        
        # Expected structure:
        # Header Marker: b"QUIC"
        # Payload Length: 4-byte big-endian integer representing len(stream_frame)
        # Checksum: 8-byte truncated SHA256 digest of stream_frame
        # Payload: stream_frame
        header_marker = b"QUIC"
        frame_length = len(stream_frame)
        length_bytes = frame_length.to_bytes(4, byteorder='big')
        checksum = hashlib.sha256(stream_frame).digest()[:8]
        expected_packet = header_marker + length_bytes + checksum + stream_frame
        
        self.assertEqual(len(self.dummy_encryptor.encrypted_packets), 1, "One encrypted packet should be produced.")
        self.assertEqual(self.dummy_encryptor.encrypted_packets[0], expected_packet,
                         "The produced QUIC packet does not match the expected format.")

    def test_send_failure(self) -> None:
        # Simulate a failure by having the TLS encryptor throw an exception.
        class FailingTLSEncryptor:
            def encrypt(self, packet: bytes) -> None:
                raise Exception("Encryption failure")
        
        quic_sender = QUICSender(tls_encryptor=FailingTLSEncryptor())
        with self.assertRaises(TransmissionError):
            quic_sender.send(b"Some stream frame")

if __name__ == '__main__':
    unittest.main()
