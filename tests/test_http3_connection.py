# pylint: disable=duplicate-code
"""
Test cases for HTTP3Connection class.
"""
import unittest
from quicpro.utils.http3.connection.http3_connection import HTTP3Connection
from tests.test_utils.dummy_quic_manager import DummyQuicManager

class TestHTTP3Connection(unittest.TestCase):
    """Test cases for the HTTP3Connection class."""
    def setUp(self):
        self.dummy_manager = DummyQuicManager()
        self.connection = HTTP3Connection(self.dummy_manager)

    """Test that the HTTP3Connection is initialized correctly."""
    def test_initialization(self):
        self.assertIsNotNone(self.connection, "HTTP3Connection should be initialized.")
        self.assertIsNotNone(self.connection.stream_manager,
                            "StreamManager should be initialized.")
        self.assertIsNotNone(self.connection.quic_sender,
                            "QUICSender should be initialized.")

    """Test that the HTTP3Connection can send a request."""
    def test_send_request(self):
        self.connection.send_request(b"TestBody")
        self.assertEqual(len(self.dummy_manager.connection.sent_packets),
                         1, "send_request should send a packet.")

    """Test that the HTTP3Connection can receive a response."""
    def test_receive_response(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(TestResponse))"
        self.connection.route_incoming_frame(packet)
        response = self.connection.receive_response()
        self.assertEqual(response, b"TestResponse",
                         "receive_response should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream error."""
    def test_handle_stream_error(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Error))"
        self.connection.route_incoming_frame(packet)
        self.connection.handle_stream_error(1)
        self.assertTrue(self.connection.stream_manager.is_stream_error(1),
                        "handle_stream_error should mark the stream as errored.")
        
    """Test that the HTTP3Connection can handle a stream close."""
    def test_handle_stream_close(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Close))"
        self.connection.route_incoming_frame(packet)
        self.connection.handle_stream_close(1)
        self.assertTrue(self.connection.stream_manager.is_stream_closed(1),
                        "handle_stream_close should mark the stream as closed.")
        
    """Test that the HTTP3Connection can handle a stream reset."""
    def test_handle_stream_reset(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Reset))"
        self.connection.route_incoming_frame(packet)
        self.connection.handle_stream_reset(1)
        self.assertTrue(self.connection.stream_manager.is_stream_reset(1),
                        "handle_stream_reset should mark the stream as reset.")

    """Test that the HTTP3Connection can handle a stream priority update."""
    def test_handle_stream_priority_update(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(PriorityUpdate))"
        self.connection.route_incoming_frame(packet)
        self.connection.handle_stream_priority_update(1)
        self.assertTrue(self.connection.stream_manager.is_stream_priority_updated(1),
                        "handle_stream_priority_update should mark the stream as priority updated.")

    """Test that the HTTP3Connection can handle a stream data frame."""
    def test_handle_stream_data_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Data))"
        self.connection.route_incoming_frame(packet)
        data = self.connection.handle_stream_data_frame(1)
        self.assertEqual(data, b"Data",
                         "handle_stream_data_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream control frame."""
    def test_handle_stream_control_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Control))"
        self.connection.route_incoming_frame(packet)
        control = self.connection.handle_stream_control_frame(1)
        self.assertEqual(control, b"Control",
                         "handle_stream_control_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream priority frame."""
    def test_handle_stream_priority_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Priority))"
        self.connection.route_incoming_frame(packet)
        priority = self.connection.handle_stream_priority_frame(1)
        self.assertEqual(priority, b"Priority",
                         "handle_stream_priority_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream cancel frame."""
    def test_handle_stream_cancel_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Cancel))"
        self.connection.route_incoming_frame(packet)
        cancel = self.connection.handle_stream_cancel_frame(1)
        self.assertEqual(cancel, b"Cancel",
                         "handle_stream_cancel_frame should return the extracted payload.")
        
    """Test that the HTTP3Connection can handle a stream settings frame."""
    def test_handle_stream_settings_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Settings))"
        self.connection.route_incoming_frame(packet)
        settings = self.connection.handle_stream_settings_frame(1)
        self.assertEqual(settings, b"Settings",
                         "handle_stream_settings_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream ping frame."""
    def test_handle_stream_ping_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Ping))"
        self.connection.route_incoming_frame(packet)
        ping = self.connection.handle_stream_ping_frame(1)
        self.assertEqual(ping, b"Ping",
                         "handle_stream_ping_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream goaway frame."""
    def test_handle_stream_goaway_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Goaway))"
        self.connection.route_incoming_frame(packet)
        goaway = self.connection.handle_stream_goaway_frame(1)
        self.assertEqual(goaway, b"Goaway",
                         "handle_stream_goaway_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream unknown frame."""
    def test_handle_stream_unknown_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Unknown))"
        self.connection.route_incoming_frame(packet)
        unknown = self.connection.handle_stream_unknown_frame(1)
        self.assertEqual(unknown, b"Unknown",
                         "handle_stream_unknown_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream data frame."""
    def test_handle_stream_data_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Data))"
        self.connection.route_incoming_frame(packet)
        data = self.connection.handle_stream_data_frame(1)
        self.assertEqual(data, b"Data",
                         "handle_stream_data_frame should return the extracted payload.")

    """Test that the HTTP3Connection can handle a stream control frame."""
    def test_handle_stream_control_frame(self):
        packet = b"\x01HTTP3Stream(stream_id=1, payload=Frame(Control))"
        self.connection.route_incoming_frame(packet)
        control = self.connection.handle_stream_control_frame(1)
        self.assertEqual(control, b"Control",
                         "handle_stream_control_frame should return the extracted payload.")

    """ Test that the HTTP3Connection can handle a request default stream. """
    def test_send_request_default_stream(self):
        self.connection.send_request(b"TestBody")
        self.assertEqual(len(self.dummy_manager.connection.sent_packets),
                         1, "send_stream should be called once.")

    """ Test that the HTTP3Connection can handle a request with a custom stream. """
    def test_send_request_with_custom_stream(self):
        self.connection.send_request(b"TestBody", stream_id=42)
        stream = self.connection.stream_manager.get_stream(42)
        self.assertIsNotNone(
            stream, "send_stream should be called once with custom stream_id.")

if __name__ == '__main__':
    unittest.main()
