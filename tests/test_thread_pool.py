"""
ThreadPool test using shared threadpool helper.
"""
import unittest
from tests.test_utils.threadpool_helper import run_threadpool_sample

class TestThreadPool(unittest.TestCase):
    def test_sample_task(self):
        executed = run_threadpool_sample()
        self.assertTrue(executed, "ThreadPool did not execute sample_task")

if __name__ == "__main__":
    unittest.main()
