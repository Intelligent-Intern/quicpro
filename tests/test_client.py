"""
Test module for the Client.
"""

import threading
import socket
import time
import unittest
from quicpro.client import Client, Response

class TestClient(unittest.TestCase):
    """Test cases for the HTTP/3 Client."""
    def setUp(self) -> None:
        """Set up the Client instance in demo mode."""
        self.client = Client(remote_address=("127.0.0.1", 9090), demo_mode=True, event_loop_max_workers=2)

    def tearDown(self) -> None:
        """Tear down the Client instance."""
        self.client.close()

    def test_request_simulated_response(self):
        """Test that the client returns a simulated response with code 200 and expected content."""
        response = self.client.request("GET", "https://example.com", params={"q": "test"})
        self.assertEqual(response.status_code, 200, "Simulated response should have status code 200.")
        self.assertEqual(response.content, "integration-test", "Response content should be 'integration-test'.")

    def test_request_stream_integration(self):
        """Test that a client request creates an associated stream."""
        _ = self.client.request("GET", "https://example.com")
        stream = self.client.http3_connection.stream_manager.get_stream(1)
        self.assertIsNotNone(stream, "A stream should be created for the client request.")

if __name__ == '__main__':
    unittest.main()
