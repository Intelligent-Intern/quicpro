import unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.sender.tls_encryptor import TLSEncryptor, TLSConfig
from quicpro.exceptions import EncryptionError

class DummyUDPSender:
    def __init__(self):
        self.sent_packets = []

    def send(self, packet: bytes) -> None:
        # Simply store the packet for later verification.
        self.sent_packets.append(packet)

class FailingUDPSender:
    def send(self, packet: bytes) -> None:
        # Simulate a UDP send failure.
        raise Exception("UDP send failure")

class TestTLSEncryptor(unittest.TestCase):
    def setUp(self) -> None:
        # Use a simple TLS configuration with all-zero key and IV.
        self.config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        self.dummy_udp_sender = DummyUDPSender()
        self.encryptor = TLSEncryptor(udp_sender=self.dummy_udp_sender, config=self.config)

    def test_encrypt_valid_packet(self) -> None:
        quic_packet = b"Test QUIC Packet"
        self.encryptor.encrypt(quic_packet)
        self.assertEqual(len(self.dummy_udp_sender.sent_packets), 1, "One packet should be sent.")

        record = self.dummy_udp_sender.sent_packets[0]
        # The record format: 8-byte sequence number followed by ciphertext.
        # For the first packet, the sequence number should be 0.
        seq_num_bytes = record[:8]
        self.assertEqual(seq_num_bytes, (0).to_bytes(8, byteorder="big"), "Sequence number should be 0 for the first packet.")
        ciphertext = record[8:]
        # Since sequence number is 0, the nonce equals config.iv (because 0.to_bytes(12) is 12 zero bytes).
        nonce = self.config.iv
        aesgcm = AESGCM(self.config.key)
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        self.assertEqual(decrypted, quic_packet, "Decrypted packet should match the original QUIC packet.")

    def test_sequence_increment(self) -> None:
        # Encrypt two packets and verify that the sequence number increments.
        quic_packet1 = b"Packet One"
        quic_packet2 = b"Packet Two"
        self.encryptor.encrypt(quic_packet1)
        self.encryptor.encrypt(quic_packet2)
        self.assertEqual(len(self.dummy_udp_sender.sent_packets), 2, "Two packets should be sent.")

        # Check that the second packet has sequence number 1.
        record2 = self.dummy_udp_sender.sent_packets[1]
        seq_num_bytes = record2[:8]
        self.assertEqual(seq_num_bytes, (1).to_bytes(8, byteorder="big"), "Sequence number should be 1 for the second packet.")

    def test_encrypt_failure(self) -> None:
        # Test that if the UDP sender fails, an EncryptionError is raised.
        failing_udp_sender = FailingUDPSender()
        encryptor = TLSEncryptor(udp_sender=failing_udp_sender, config=self.config)
        with self.assertRaises(EncryptionError):
            encryptor.encrypt(b"Some packet")

if __name__ == '__main__':
    unittest.main()
