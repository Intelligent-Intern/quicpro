import unittest
import threading
from quicpro.utils.http3.streams.stream_manager import StreamManager

class TestStreamManager(unittest.TestCase):
    def setUp(self):
        self.manager = StreamManager()
    def test_create_stream(self):
        stream = self.manager.create_stream()
        self.assertIsNotNone(stream, "Created stream should not be None.")
        self.assertEqual(stream.state, "open", "Newly created stream should be 'open'.")
    def test_get_stream(self):
        stream = self.manager.create_stream()
        retrieved = self.manager.get_stream(stream.stream_id)
        self.assertIsNotNone(retrieved, "Should be able to retrieve the stream by its ID.")
        self.assertEqual(stream.stream_id, retrieved.stream_id, "Stream IDs should match.")
    def test_close_stream(self):
        stream = self.manager.create_stream()
        self.manager.close_stream(stream.stream_id)
        retrieved = self.manager.get_stream(stream.stream_id)
        self.assertIsNone(retrieved, "Closed stream should not be retrievable.")
        self.assertEqual(stream.state, "closed", "Stream state should be 'closed' after closing.")
    def test_thread_safety(self):
        num_threads = 50
        created_ids = []
        lock = threading.Lock()
        def create_stream():
            s = self.manager.create_stream()
            with lock:
                created_ids.append(s.stream_id)
        threads = [threading.Thread(target=create_stream) for _ in range(num_threads)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.assertEqual(len(created_ids), num_threads, "Every thread should create one stream.")
        self.assertEqual(len(set(created_ids)), num_threads, "All stream IDs must be unique.")

if __name__ == '__main__':
    unittest.main()
