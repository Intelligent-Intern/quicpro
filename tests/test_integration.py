import os
import socket
import threading
import tempfile
import time
import unittest
from quicpro.sender.producer_app import ProducerApp
from quicpro.sender.encoder import Encoder
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.sender.quic_sender import QUICSender
from quicpro.sender.tls_encryptor import TLSEncryptor, TLSConfig
from quicpro.sender.udp_sender import UDPSender
from quicpro.sender.network import Network
from quicpro.receiver.decoder import Decoder
from quicpro.receiver.http3_receiver import HTTP3Receiver
from quicpro.receiver.quic_receiver import QUICReceiver
from quicpro.receiver.tls_decryptor import TLSDecryptor
from quicpro.receiver.udp_receiver import UDPReceiver


class FileWritingConsumer:
    """A consumer that writes received messages to a file."""
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def consume(self, message: str) -> None:
        with open(self.filename, 'w') as f:
            f.write(message)


class TestIntegrationPipeline(unittest.TestCase):
    """End-to-end integration tests for the complete pipeline."""
    
    def setUp(self) -> None:
        # Create a temporary file for output.
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.consumer_app = FileWritingConsumer(filename=self.temp_file.name)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_end_to_end_pipeline_file_write(self) -> None:
        """
        Test the entire pipeline from message production to consumer file writing.
        """
        # Build the receiver pipeline.
        decoder = Decoder(consumer_app=self.consumer_app)
        http3_receiver = HTTP3Receiver(decoder=decoder)
        quic_receiver = QUICReceiver(http3_receiver=http3_receiver)
        default_config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        tls_decryptor = TLSDecryptor(quic_receiver=quic_receiver, config=default_config)
        bind_address = ("127.0.0.1", 9091)
        udp_receiver = UDPReceiver(bind_address=bind_address, tls_decryptor=tls_decryptor)

        def receiver_thread_func() -> None:
            # To simulate proper encryption, construct a dummy QUIC packet.
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            aesgcm = AESGCM(default_config.key)
            # Build a dummy QUIC packet with header "QUICFRAME:dummy:0:1:HTTP3:" followed by the payload.
            dummy_payload = b"integration-test"
            dummy_quic_packet = b"QUICFRAME:dummy:0:1:HTTP3:Frame(" + dummy_payload + b")\n"
            nonce = default_config.iv  # For seq number 0.
            ciphertext = aesgcm.encrypt(nonce, dummy_quic_packet, None)
            encrypted_packet = b"\x00" * 8 + ciphertext
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(bind_address)
                sock.sendto(encrypted_packet, bind_address)
                # Optionally, receive the packet so that tls_decryptor.decrypt is triggered.
                data, _ = sock.recvfrom(4096)
                tls_decryptor.decrypt(data)

        receiver_thread = threading.Thread(target=receiver_thread_func, daemon=True)
        receiver_thread.start()

        # Build the sender pipeline.
        network = Network(remote_address=bind_address, timeout=5.0)
        udp_sender = UDPSender(network=network)
        tls_encryptor = TLSEncryptor(udp_sender=udp_sender, config=default_config)
        quic_sender = QUICSender(tls_encryptor=tls_encryptor)
        http3_sender = HTTP3Sender(quic_sender=quic_sender, stream_id=9)
        encoder = Encoder(http3_sender=http3_sender)
        producer_app = ProducerApp(encoder=encoder)

        # Trigger message creation through the pipeline.
        producer_app.create_message("integration-test")
        network.close()
        receiver_thread.join(timeout=2)
        time.sleep(1)  # Allow asynchronous processing to complete.
        self.assertTrue(os.path.exists(self.temp_file.name), "The consumer output file was not created.")
        with open(self.temp_file.name, 'r') as f:
            content = f.read()
        self.assertEqual(content, "integration-test", "The file content does not match the expected message.")


if __name__ == '__main__':
    unittest.main()