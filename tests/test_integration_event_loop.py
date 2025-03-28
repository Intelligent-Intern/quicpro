"""
Test module for end-to-end integration of the synchronous event loop.
"""

import time
import threading
from quicpro.utils.event_loop.sync_loop import SyncEventLoop

def test_integration_event_loop():
    results = []
    def task(i):
        results.append(i)
    loop = SyncEventLoop(max_workers=2)
    loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
    loop_thread.start()
    for i in range(5):
        loop.schedule_task(task, i)
    time.sleep(0.2)
    loop.stop()
    loop_thread.join()
    assert results == [0, 1, 2, 3, 4], f"Not all tasks executed correctly: {results}"

if __name__ == "__main__":
    test_integration_event_loop()
    print("Integration event loop test passed")
