import unittest
from quicpro.sender.encoder import Encoder, Message
from quicpro.sender.http3_sender import HTTP3Sender
from quicpro.exceptions import TransmissionError

class DummyTLSEncryptor:
    def __init__(self):
        self.received_packet = None
    def encrypt(self, packet: bytes) -> None:
        self.received_packet = packet

class DummyQUICSender:
    def __init__(self, tls_encryptor: DummyTLSEncryptor):
        self.tls_encryptor = tls_encryptor
        self.sent_frame = None
    def send(self, frame: bytes) -> None:
        self.sent_frame = frame
        packet = b"QUICFRAME:dummy:0:1:HTTP3:" + frame
        self.tls_encryptor.encrypt(packet)

class DummyHTTP3Sender:
    def __init__(self, quic_sender: DummyQUICSender, stream_id: int):
        self.quic_sender = quic_sender
        self.stream_id = stream_id
    def send(self, frame: bytes) -> None:
        stream_frame = b"HTTP3Stream(stream_id=%d, payload=" % self.stream_id + frame + b")"
        self.quic_sender.send(stream_frame)

class TestSenderPipeline(unittest.TestCase):
    def setUp(self):
        self.dummy_encryptor = DummyTLSEncryptor()
        self.dummy_quic_sender = DummyQUICSender(tls_encryptor=self.dummy_encryptor)
        self.dummy_http3_sender = DummyHTTP3Sender(quic_sender=self.dummy_quic_sender, stream_id=9)
    def test_sender_pipeline(self):
        encoder = Encoder(http3_sender=self.dummy_http3_sender)
        encoder.encode(Message(content="test"))
        self.assertIsNotNone(self.dummy_encryptor.received_packet,
                             "TLS encryptor did not receive any packet.")
        self.assertIn(b"Frame(test)", self.dummy_encryptor.received_packet,
                      "The encoded frame is missing from the TLS packet.")

if __name__ == '__main__':
    unittest.main()