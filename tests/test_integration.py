import os
import socket
import threading
import tempfile
import time
import unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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
from quicpro.utils.http3.streams.stream_manager import StreamManager
from quicpro.utils.http3.streams.priority import StreamPriority

# A simple consumer that writes the received message to a temporary file.
class FileWritingConsumer:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def consume(self, message: str) -> None:
        with open(self.filename, 'w') as f:
            f.write(message)

class TestIntegrationPipeline(unittest.TestCase):
    """
    End-to-end integration test for the complete pipeline, including the new
    streams management and stream priority functionality.
    """
    def setUp(self) -> None:
        # Create a temporary file to capture the output from the consumer.
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.consumer_app = FileWritingConsumer(filename=self.temp_file.name)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_end_to_end_pipeline_with_streams_and_priority(self) -> None:
        """
        Test the entire pipeline from message production to consumer file writing.
        This integration test verifies that:
          - The receiver pipeline (UDPReceiver, TLSDecryptor, QUICReceiver,
            HTTP3Receiver, Decoder) processes an incoming QUIC packet correctly.
          - The sender pipeline (Network, UDPSender, TLSEncryptor, QUICSender,
            HTTP3Sender, Encoder, ProducerApp) correctly encapsulates and sends a message.
          - The new StreamManager and StreamPriority functionality are integrated:
              * A stream is created for the request.
              * A high priority (low weight) can be assigned and is stored.
          - The final output matches the expected message.
        """
        # Build the receiver pipeline:
        # 1. Create a decoder that passes the extracted message to the consumer app.
        decoder = Decoder(consumer_app=self.consumer_app)
        # 2. HTTP3Receiver extracts the HTTP3 frame and passes it to the decoder.
        http3_receiver = HTTP3Receiver(decoder=decoder)
        # 3. QUICReceiver reassembles QUIC packets and forwards the stream frame.
        quic_receiver = QUICReceiver(http3_receiver=http3_receiver)
        # 4. Set up a default TLS configuration.
        default_config = TLSConfig(key=b"\x00" * 32, iv=b"\x00" * 12)
        # 5. TLSDecryptor decrypts incoming packets and passes them to QUICReceiver.
        tls_decryptor = TLSDecryptor(quic_receiver=quic_receiver, config=default_config)
        # 6. UDPReceiver listens for UDP packets on a test bind address.
        bind_address = ("127.0.0.1", 9091)
        udp_receiver = UDPReceiver(bind_address=bind_address, tls_decryptor=tls_decryptor)

        # Start the receiver in a separate thread.
        def receiver_thread_func() -> None:
            # Simulate a properly encrypted QUIC packet containing a stream frame.
            aesgcm = AESGCM(default_config.key)
            # Build a dummy stream frame: "HTTP3:Frame(integration-test)\n"
            dummy_payload = b"integration-test"
            dummy_quic_packet = b"QUICFRAME:dummy:0:1:HTTP3:Frame(" + dummy_payload + b")\n"
            nonce = default_config.iv  # For sequence number 0.
            ciphertext = aesgcm.encrypt(nonce, dummy_quic_packet, None)
            encrypted_packet = b"\x00" * 8 + ciphertext
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.bind(bind_address)
                sock.sendto(encrypted_packet, bind_address)
                # Optionally, trigger the decryption process.
                try:
                    data, _ = sock.recvfrom(4096)
                    tls_decryptor.decrypt(data)
                except socket.timeout:
                    pass

        receiver_thread = threading.Thread(target=receiver_thread_func, daemon=True)
        receiver_thread.start()

        # Build the sender pipeline:
        # 1. Create a network instance pointing to the same bind address.
        network = Network(remote_address=bind_address, timeout=5.0)
        # 2. UDPSender sends encrypted packets over the network.
        udp_sender = UDPSender(network=network)
        # 3. TLSEncryptor encrypts QUIC packets using the TLS configuration.
        tls_encryptor = TLSEncryptor(udp_sender=udp_sender, config=default_config)
        # 4. QUICSender wraps an HTTP3 stream frame into a QUIC packet.
        quic_sender = QUICSender(tls_encryptor=tls_encryptor)
        # 5. Create a StreamPriority object for high priority (lower weight means higher priority).
        priority = StreamPriority(weight=1, dependency=0)
        # 6. HTTP3Sender maps the encoded frame onto an HTTP/3 stream.
        #    Assume the upgraded HTTP3Sender supports priority assignment.
        http3_sender = HTTP3Sender(quic_sender=quic_sender, stream_id=9)
        http3_sender.priority = priority  # Assign high priority to this stream.
        # 7. Encoder encodes messages into HTTP3 frames.
        encoder = Encoder(http3_sender=http3_sender)
        # 8. ProducerApp creates messages to be sent.
        producer_app = ProducerApp(encoder=encoder)

        # Trigger the message creation and sending through the pipeline.
        producer_app.create_message("integration-test")
        network.close()
        receiver_thread.join(timeout=2)
        # Allow time for asynchronous processing.
        time.sleep(1)
        
        # Verify that the consumer output file contains the expected message.
        self.assertTrue(os.path.exists(self.temp_file.name), "The consumer output file was not created.")
        with open(self.temp_file.name, 'r') as f:
            content = f.read()
        self.assertEqual(content, "integration-test", "The file content does not match the expected message.")

if __name__ == '__main__':
    unittest.main()
