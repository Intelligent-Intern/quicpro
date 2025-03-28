#!/usr/bin/env python
"""
Example to run the synchronous event loop.
"""

import threading
import time
from quicpro.utils.event_loop.sync_loop import SyncEventLoop

def sample_task():
    """A simple task that prints a message."""
    print("Task executed")

def main():
    """Run the synchronous event loop with a sample task."""
    loop = SyncEventLoop(max_workers=2)
    loop.schedule_task(sample_task)
    loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
    loop_thread.start()
    time.sleep(1)
    loop.stop()
    loop_thread.join()

if __name__ == "__main__":
    main()
