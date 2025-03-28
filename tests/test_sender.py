import unittest
from quicpro.sender.encoder import Encoder, Message
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.sender.quic_sender import QUICSender
from quicpro.sender.tls_encryptor import TLSEncryptor, TLSConfig
from quicpro.sender.udp_sender import UDPSender
from quicpro.sender.network import Network
from quicpro.sender.producer_app import ProducerApp


class DummyTLSEncryptor:
    def __init__(self) -> None:
        self.received_packet = None

    def encrypt(self, quic_packet: bytes) -> None:
        self.received_packet = quic_packet


class DummyQUICSender:
    def __init__(self, tls_encryptor: DummyTLSEncryptor) -> None:
        self.tls_encryptor = tls_encryptor
        self.received_frame = None

    def send(self, stream_frame: bytes) -> None:
        self.received_frame = stream_frame
        # Simulate wrapping the HTTP/3 stream frame into a QUIC packet.
        packet = b"QUICFRAME:dummy:0:1:HTTP3:" + stream_frame
        self.tls_encryptor.encrypt(packet)


class DummyHTTP3Sender:
    def __init__(self, quic_sender: DummyQUICSender, stream_id: int) -> None:
        self.quic_sender = quic_sender
        self.stream_id = stream_id

    def send(self, frame: bytes) -> None:
        # Construct a dummy HTTP/3 stream frame.
        stream_frame = b"HTTP3Stream(stream_id=%d, payload=" % self.stream_id + frame + b")"
        self.quic_sender.send(stream_frame)


class TestSenderPipeline(unittest.TestCase):
    """Unit tests for the sender pipeline components."""
    
    def test_sender_pipeline(self) -> None:
        dummy_tls = DummyTLSEncryptor()
        dummy_quic = DummyQUICSender(tls_encryptor=dummy_tls)
        dummy_http3 = DummyHTTP3Sender(quic_sender=dummy_quic, stream_id=9)
        encoder = Encoder(http3_sender=dummy_http3)
        producer = ProducerApp(encoder=encoder)
        # Trigger a message creation through the full sender pipeline.
        producer.create_message("test")
        self.assertIsNotNone(dummy_tls.received_packet,
                             "TLS encryptor did not receive any packet.")
        self.assertIn(b"Frame(test)", dummy_tls.received_packet,
                      "The encoded frame is missing from the TLS packet.")
        self.assertIn(b"HTTP3Stream", dummy_tls.received_packet,
                      "The HTTP/3 stream frame is missing in the TLS packet.")
        self.assertIn(b"QUICFRAME", dummy_tls.received_packet,
                      "The QUIC packet header is missing in the TLS packet.")


if __name__ == '__main__':
    unittest.main()