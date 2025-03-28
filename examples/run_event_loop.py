#!/usr/bin/env python
from quicpro.utils.event_loop.sync_loop import SyncEventLoop
import time

def sample_task():
    print("Task executed at", time.time())

def main():
    loop = SyncEventLoop(max_workers=2)
    loop.schedule_task(sample_task)
    # Run for a short period to let the task execute, then stop.
    threading.Thread(target=loop.run_forever, daemon=True).start()
    time.sleep(1)
    loop.stop()

if __name__ == "__main__":
    main()