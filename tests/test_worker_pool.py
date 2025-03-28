"""
Test module for the ThreadPool wrapper.
"""

import time
from quicpro.utils.event_loop.thread_pool import ThreadPool

def test_thread_pool():
    task_executed = False

    def sample_task():
        nonlocal task_executed
        task_executed = True

    pool = ThreadPool(max_workers=2)
    future = pool.submit(sample_task)
    future.result(timeout=1)
    pool.shutdown()
    assert task_executed, "ThreadPool did not execute sample_task"

if __name__ == "__main__":
    test_thread_pool()
    print("ThreadPool test passed")
