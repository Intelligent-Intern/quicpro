"""
Test module for the TLS Encryptor.
"""

import unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.sender.tls_encryptor import TLSEncryptor, TLSConfig
from quicpro.exceptions import EncryptionError

class DummyUDPSender:
    def __init__(self):
        self.sent_packets = []
    def send(self, packet: bytes) -> None:
        self.sent_packets.append(packet)

class FailingUDPSender:
    def send(self, packet: bytes) -> None:
        raise Exception("UDP send failure")

class TestTLSEncryptor(unittest.TestCase):
    def setUp(self) -> None:
        # Use all-zero key and IV for simplicity.
        self.config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        self.dummy_udp_sender = DummyUDPSender()
        # Create an encryptor in demo mode.
        self.encryptor = TLSEncryptor(udp_sender=self.dummy_udp_sender, config=self.config, demo=True)

    def test_encrypt_valid_packet(self):
        quic_packet = b"Test QUIC Packet"
        self.encryptor.encrypt(quic_packet)
        self.assertEqual(len(self.dummy_udp_sender.sent_packets), 1, "One UDP packet should be sent.")
        record = self.dummy_udp_sender.sent_packets[0]
        # Expect an 8-byte sequence number at the beginning.
        seq_num_bytes = record[:8]
        self.assertEqual(seq_num_bytes, (0).to_bytes(8, "big"), "Sequence number should be 0 for first packet.")
        ciphertext = record[8:]
        # Decrypt the packet using AESGCM with the same key and nonce.
        aesgcm = AESGCM(self.config.key)
        # In demo mode, sequence number zero implies nonce equals config.iv.
        nonce = self.config.iv
        decrypted = aesgcm.decrypt(nonce, ciphertext, None)
        self.assertEqual(decrypted, quic_packet, "Decrypted packet should match the original QUIC packet.")

    def test_encrypt_failure(self):
        failing_udp_sender = FailingUDPSender()
        encryptor = TLSEncryptor(udp_sender=failing_udp_sender, config=self.config, demo=True)
        with self.assertRaises(EncryptionError):
            encryptor.encrypt(b"Some packet")

if __name__ == '__main__':
    unittest.main()
