import threading
import socket
import time
import unittest
from quicpro.client import Client, Response

class TestClientEventLoop(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Client(remote_address=("127.0.0.1", 9090), demo_mode=True, event_loop_max_workers=2)
    
    def tearDown(self) -> None:
        self.client.close()
    
    def test_client_event_loop(self):
        response = self.client.request("GET", "https://example.com")
        self.assertEqual(response.status_code, 200, "Simulated response should have status code 200.")
        self.assertEqual(response.content, "integration-test", "Response content should be 'integration-test'.")

if __name__ == '__main__':
    unittest.main()