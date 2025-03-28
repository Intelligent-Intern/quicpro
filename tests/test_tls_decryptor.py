"""
Test module for the TLSDecryptor.
"""

import unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.model.tls_config import TLSConfig
from quicpro.exceptions import DecryptionError

class DummyQUICReceiver:
    def __init__(self):
        self.received_packets = []
    def receive(self, packet: bytes) -> None:
        self.received_packets.append(packet)

class TestTLSDecryptor(unittest.TestCase):
    def setUp(self):
        # Use an all-zero key and IV for testing.
        self.config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        self.dummy_receiver = DummyQUICReceiver()
        from quicpro.receiver.tls_decryptor import TLSDecryptor
        self.decryptor = TLSDecryptor(quic_receiver=self.dummy_receiver, config=self.config)
        self.aesgcm = AESGCM(self.config.key)

    def test_decrypt_valid_packet(self):
        quic_packet = b"Test QUIC Packet"
        # For sequence number 0, nonce equals config.iv.
        nonce = self.config.iv
        ciphertext = self.aesgcm.encrypt(nonce, quic_packet, None)
        # Prepend an 8-byte sequence number (0) to mimic demo mode packet structure.
        encrypted_packet = (0).to_bytes(8, byteorder="big") + ciphertext
        self.decryptor.decrypt(encrypted_packet)
        self.assertEqual(len(self.dummy_receiver.received_packets), 1, "One decrypted packet should be received.")
        self.assertEqual(self.dummy_receiver.received_packets[0], quic_packet, "Decrypted packet does not match the original.")

    def test_decrypt_failure(self):
        with self.assertRaises(DecryptionError):
            # Provide an encrypted packet that is too short.
            self.decryptor.decrypt(b"\x00")

if __name__ == '__main__':
    unittest.main()
