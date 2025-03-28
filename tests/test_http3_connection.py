import unittest
from quicpro.utils.http3.connection.http3_connection import HTTP3Connection

# DummyQuicManager simulates the behavior of the real QuicManager
# for the purpose of testing HTTP3Connection.
class DummyQuicManager:
    def __init__(self):
        self.sent_stream_calls = []
        self.received_packets = []
        # Optionally, you could simulate a stream manager here if needed.
    
    def send_stream(self, stream_id, stream_frame):
        # Record the call for later assertions.
        self.sent_stream_calls.append((stream_id, stream_frame))
    
    def receive_packet(self, packet):
        # Record the received packet for later assertions.
        self.received_packets.append(packet)

class TestHTTP3Connection(unittest.TestCase):
    def setUp(self):
        # Initialize the dummy manager and the HTTP3Connection with it.
        self.dummy_manager = DummyQuicManager()
        self.connection = HTTP3Connection(self.dummy_manager)

    def test_negotiate_settings(self):
        # Test that settings negotiation updates the connection's settings.
        settings = {"max_header_list_size": 16384, "qpack_max_table_capacity": 4096}
        self.connection.negotiate_settings(settings)
        self.assertEqual(self.connection.settings, settings,
                         "Negotiated settings should be stored in the connection.")

    def test_send_request_default_stream(self):
        # Test that send_request delegates to the dummy manager with default stream_id.
        request_data = b"GET /index.html HTTP/3"
        self.connection.send_request(request_data)
        self.assertEqual(len(self.dummy_manager.sent_stream_calls), 1,
                         "send_stream should be called once.")
        stream_id, stream_frame = self.dummy_manager.sent_stream_calls[0]
        self.assertEqual(stream_id, 1, "Default stream_id should be 1.")
        self.assertEqual(stream_frame, request_data,
                         "Request data should be passed correctly to send_stream.")

    def test_send_request_with_custom_stream(self):
        # Test that send_request uses the provided stream_id when specified.
        request_data = b"POST /submit HTTP/3"
        custom_stream_id = 42
        self.connection.send_request(request_data, stream_id=custom_stream_id)
        self.assertEqual(len(self.dummy_manager.sent_stream_calls), 1,
                         "send_stream should be called once with custom stream_id.")
        stream_id, stream_frame = self.dummy_manager.sent_stream_calls[0]
        self.assertEqual(stream_id, custom_stream_id,
                         "Custom stream_id should be used in send_stream.")
        self.assertEqual(stream_frame, request_data,
                         "Request data should be passed correctly to send_stream.")

    def test_receive_response(self):
        # Test that receive_response correctly delegates packet reception.
        packet = b"Dummy packet data for response"
        self.connection.receive_response(packet)
        self.assertEqual(len(self.dummy_manager.received_packets), 1,
                         "receive_packet should be called once.")
        self.assertEqual(self.dummy_manager.received_packets[0], packet,
                         "The received packet should match the sent packet.")

if __name__ == '__main__':
    unittest.main()
