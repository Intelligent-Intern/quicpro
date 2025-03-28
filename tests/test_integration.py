"""
Test module for end-to-end integration pipeline using the HTTP/3 client.
"""

import os
import tempfile
import time
import unittest
from quicpro.client import Client

class TestIntegrationPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.expected_output = "integration-test"

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_end_to_end_pipeline_with_streams_and_priority(self):
        from quicpro.utils.http3.streams.priority import StreamPriority
        client = Client(remote_address=("127.0.0.1", 9091), timeout=5, event_loop_max_workers=2, demo_mode=True)
        response = client.request("GET", "https://example.com?priority=high", priority=StreamPriority(1, dependency=0))
        self.assertEqual(response.status_code, 200, "Simulated response should have status code 200.")
        self.assertEqual(response.content, self.expected_output, "Consumer output does not match expected value.")
        client.close()

if __name__ == '__main__':
    unittest.main()
