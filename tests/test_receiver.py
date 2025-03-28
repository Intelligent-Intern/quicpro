import unittest
from quicpro.receiver.consumer_app import ConsumerApp
from quicpro.receiver.decoder import Decoder
from quicpro.receiver.http3_receiver import HTTP3Receiver
from quicpro.receiver.quic_receiver import QUICReceiver
from quicpro.receiver.tls_decryptor import TLSDecryptor
from quicpro.receiver.udp_receiver import UDPReceiver
from quicpro.sender.tls_encryptor import TLSConfig
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class DummyConsumerApp:
    def __init__(self) -> None:
        self.received_message = None

    def consume(self, message: str) -> None:
        self.received_message = message


class DummyUDPReceiver(UDPReceiver):
    def listen_once(self, data: bytes) -> None:
        """Directly process a single packet for testing purposes."""
        self.tls_decryptor.decrypt(data)


class TestReceiverPipeline(unittest.TestCase):
    """Unit tests for the receiver pipeline components."""
    
    def test_receiver_pipeline(self) -> None:
        dummy_consumer = DummyConsumerApp()
        decoder = Decoder(consumer_app=dummy_consumer)
        http3_receiver = HTTP3Receiver(decoder=decoder)
        quic_receiver = QUICReceiver(http3_receiver=http3_receiver)
        default_config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        tls_decryptor = TLSDecryptor(quic_receiver=quic_receiver, config=default_config)
        udp_receiver = DummyUDPReceiver(bind_address=("127.0.0.1", 9090), tls_decryptor=tls_decryptor)
        # Build a dummy QUIC packet with proper header.
        dummy_payload = b"Frame(test)"
        dummy_quic_packet = b"QUICFRAME:dummy:0:1:HTTP3:" + dummy_payload
        aesgcm = AESGCM(default_config.key)
        nonce = default_config.iv  # For sequence number 0.
        ciphertext = aesgcm.encrypt(nonce, dummy_quic_packet, None)
        encrypted_packet = b"\x00" * 8 + ciphertext
        udp_receiver.listen_once(encrypted_packet)
        self.assertEqual(dummy_consumer.received_message, "test",
                         "The decoded message did not match the expected value.")


if __name__ == '__main__':
    unittest.main()