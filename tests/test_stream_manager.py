import unittest
import threading
from time import sleep

from quicpro.utils.http3.streams.stream_manager import StreamManager
from quicpro.utils.http3.streams.priority import StreamPriority

# It is assumed that the actual Stream objects created by StreamManager have at least:
#   - a "stream_id" attribute (int)
#   - a "state" attribute (e.g., "open", "closed")
#   - a "buffer" attribute (initially empty bytes)
#   - methods "send_data(data: bytes)" and "close()"
#
# The following tests cover:
#   - Creation of streams with unique IDs and correct initial state.
#   - Retrieval of streams by ID.
#   - Correct closure of streams and removal from the manager.
#   - Buffering functionality in streams.
#   - Validation and ordering of StreamPriority objects.
#   - Thread safety of stream creation under concurrent access.

class TestStreamManager(unittest.TestCase):
    def setUp(self):
        # Initialize a new StreamManager instance before each test.
        self.manager = StreamManager()

    def test_create_stream(self):
        # Test that a new stream is created with a unique id and is in the 'open' state.
        stream = self.manager.create_stream()
        self.assertIsNotNone(stream, "Created stream should not be None.")
        self.assertTrue(hasattr(stream, "stream_id"), "Stream should have a 'stream_id' attribute.")
        self.assertIsInstance(stream.stream_id, int, "Stream ID should be an integer.")
        self.assertEqual(stream.state, "open", "Newly created stream should be in 'open' state.")

    def test_get_stream(self):
        # Create a stream and retrieve it by its ID.
        stream = self.manager.create_stream()
        retrieved = self.manager.get_stream(stream.stream_id)
        self.assertIsNotNone(retrieved, "Should be able to retrieve the stream by its ID.")
        self.assertEqual(stream.stream_id, retrieved.stream_id, "Retrieved stream must have the same ID.")
        self.assertEqual(stream.state, retrieved.state, "Retrieved stream must have the same state.")

    def test_close_stream(self):
        # Create a stream, close it via the manager, and verify that it is removed.
        stream = self.manager.create_stream()
        self.manager.close_stream(stream.stream_id)
        retrieved = self.manager.get_stream(stream.stream_id)
        self.assertIsNone(retrieved, "Closed stream should not be retrievable from the manager.")
        # Also check that the stream's own state is updated to 'closed'.
        self.assertEqual(stream.state, "closed", "Stream state should be 'closed' after closing.")

    def test_stream_buffering(self):
        # Test that a stream buffers data correctly.
        stream = self.manager.create_stream()
        test_data = b"Test data for buffering"
        stream.send_data(test_data)
        self.assertEqual(stream.buffer, test_data, "Stream buffer should contain the sent data.")
        # Append additional data and check that the buffer concatenates correctly.
        more_data = b" and more data"
        stream.send_data(more_data)
        self.assertEqual(stream.buffer, test_data + more_data, "Stream buffer should correctly append new data.")

    def test_stream_priority(self):
        # Test the StreamPriority class for correct validation and ordering.
        # Create several StreamPriority objects with different weights.
        # Lower weight implies higher priority.
        p1 = StreamPriority(weight=10, dependency=0)
        p2 = StreamPriority(weight=1, dependency=0)
        p3 = StreamPriority(weight=5, dependency=0)
        priorities = [p1, p2, p3]
        sorted_priorities = sorted(priorities)
        # Expected order: p2 (weight 1), p3 (weight 5), p1 (weight 10)
        self.assertEqual(sorted_priorities, [p2, p3, p1], "StreamPriority objects should be sorted by ascending weight.")

        # Test invalid weight values: weights must be within an allowed range (e.g., 1 to 256).
        with self.assertRaises(ValueError, msg="Weight 0 should be invalid."):
            StreamPriority(weight=0, dependency=0)
        with self.assertRaises(ValueError, msg="Weight 300 should be invalid."):
            StreamPriority(weight=300, dependency=0)

    def test_thread_safety(self):
        # Test concurrent creation of streams to ensure thread safety.
        num_threads = 50
        created_ids = []
        lock = threading.Lock()

        def create_stream():
            stream = self.manager.create_stream()
            with lock:
                created_ids.append(stream.stream_id)

        threads = [threading.Thread(target=create_stream) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify that the number of streams equals the number of threads and that IDs are unique.
        self.assertEqual(len(created_ids), num_threads, "Every thread should create one stream.")
        self.assertEqual(len(set(created_ids)), num_threads, "All stream IDs must be unique.")

if __name__ == '__main__':
    unittest.main()
