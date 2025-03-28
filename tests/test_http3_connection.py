import unittest
from quicpro.utils.http3.connection.http3_connection import HTTP3Connection
from quicpro.utils.quic.quic_manager import QuicManager

class DummyConnection:
    def __init__(self):
        self.sent_packets = []
        self.is_open = True
    def send_packet(self, packet: bytes) -> None:
        self.sent_packets.append(packet)
    def close(self):
        self.is_open = False

class DummyQuicManager:
    def __init__(self):
        self.connection = DummyConnection()

class TestHTTP3Connection(unittest.TestCase):
    def setUp(self):
        self.dummy_manager = DummyQuicManager()
        self.connection = HTTP3Connection(self.dummy_manager)
    
    def test_receive_response(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(TestResponse))"
        self.connection.route_incoming_frame(packet)
        response = self.connection.receive_response()
        self.assertEqual(response, b"TestResponse", "receive_response should return the extracted payload.")

    def test_send_request_default_stream(self):
        self.connection.send_request(b"TestBody")
        self.assertEqual(len(self.dummy_manager.connection.sent_packets), 1, "send_stream should be called once.")

    def test_send_request_with_custom_stream(self):
        self.connection.send_request(b"TestBody", stream_id=42)
        stream = self.connection.stream_manager.get_stream(42)
        self.assertIsNotNone(stream, "send_stream should be called once with custom stream_id.")

if __name__ == '__main__':
    unittest.main()
