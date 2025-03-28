"""
Test module for the task scheduler.
"""

import time
import threading
from quicpro.utils.event_loop.sync_loop import SyncEventLoop
from quicpro.utils.scheduler.task_scheduler import TaskScheduler

def test_task_scheduler():
    task_executed = False

    def scheduled_task():
        nonlocal task_executed
        task_executed = True

    loop = SyncEventLoop(max_workers=2)
    scheduler = TaskScheduler(loop)

    def periodic_scheduler():
        while loop.running:
            scheduler.run_pending()
            time.sleep(0.01)

    loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
    loop_thread.start()
    scheduler_thread = threading.Thread(target=periodic_scheduler, daemon=True)
    scheduler_thread.start()

    scheduler.schedule(0.1, scheduled_task)
    time.sleep(0.2)
    loop.stop()
    loop_thread.join()
    assert task_executed, "Scheduled task did not execute"

if __name__ == "__main__":
    test_task_scheduler()
    print("Task Scheduler test passed")
