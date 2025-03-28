import unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from quicpro.sender.tls_encryptor import TLSEncryptor, TLSConfig
from quicpro.exceptions import EncryptionError

# Dummy QUIC receiver to capture decrypted packets.
class DummyQUICReceiver:
    def __init__(self):
        self.received_packets = []
    def receive(self, packet: bytes) -> None:
        self.received_packets.append(packet)

class TestTLSDecryptor(unittest.TestCase):
    def setUp(self):
        # Use a TLS configuration with an all-zero key and IV.
        self.config = TLSConfig(key=b'\x00' * 32, iv=b'\x00' * 12)
        self.dummy_receiver = DummyQUICReceiver()
        from quicpro.receiver.tls_decryptor import TLSDecryptor
        self.decryptor = TLSDecryptor(quic_receiver=self.dummy_receiver, config=self.config)
        self.aesgcm = AESGCM(self.config.key)
    
    def test_decrypt_valid_packet(self):
        # Prepare a dummy QUIC packet.
        quic_packet = b"Test QUIC Packet"
        # For sequence number 0, nonce equals the IV.
        nonce = self.config.iv
        ciphertext = self.aesgcm.encrypt(nonce, quic_packet, None)
        # Prepend an 8-byte sequence number (0).
        encrypted_packet = b"\x00" * 8 + ciphertext
        # Decrypt the packet.
        self.decryptor.decrypt(encrypted_packet)
        # Verify that the dummy receiver got the original packet.
        self.assertEqual(len(self.dummy_receiver.received_packets), 1)
        self.assertEqual(self.dummy_receiver.received_packets[0], quic_packet)

if __name__ == '__main__':
    unittest.main()
