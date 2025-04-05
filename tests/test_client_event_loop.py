# pylint: disable=duplicate-code
"""
Test module for the client event loop integration.
"""

import unittest
from quicpro.client import Client

class TestClientEventLoop(unittest.TestCase):
    """Test cases for the client event loop functionality."""
    def setUp(self) -> None:
        """Set up a Client instance for testing."""
        self.client = Client(remote_address=("127.0.0.1", 9090),
                             demo_mode=True, event_loop_max_workers=2)

    """Set up a dummy QUIC sender for the client."""
    def tearDown(self) -> None:
        """Clean up by closing the Client."""
        self.client.close()

    """Test that the client can send a request and receive a simulated response."""
    def test_client_event_loop(self):
        """Test that the client's event loop produces the expected simulated response."""
        response = self.client.request("GET", "https://example.com")
        self.assertEqual(response.status_code, 200,
                         "Simulated response should have status code 200.")
        self.assertEqual(response.content, "integration-test",
                         "Response content should be 'integration-test'.")

if __name__ == '__main__':
    unittest.main()
