import time
import threading
from quicpro.utils.event_loop.sync_loop import SyncEventLoop
from quicpro.utils.scheduler.worker_pool import WorkerPool  # Note: adjust import path if needed

def test_worker_pool():
    task_executed = False

    def worker_task():
        nonlocal task_executed
        task_executed = True

    loop = SyncEventLoop(max_workers=2)
    worker_pool = WorkerPool(num_workers=2, event_loop=loop)

    loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
    loop_thread.start()

    worker_pool.submit(worker_task)
    time.sleep(0.1)

    loop.stop()
    loop_thread.join()

    assert task_executed, "WorkerPool did not execute the task"

if __name__ == '__main__':
    test_worker_pool()
    print("WorkerPool test passed")