import time
import threading
from quicpro.utils.event_loop.sync_loop import SyncEventLoop

task_executed = False

def test_task():
    global task_executed
    task_executed = True

def main():
    global task_executed
    task_executed = False
    loop = SyncEventLoop(max_workers=2)
    loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
    loop_thread.start()
    
    loop.schedule_task(test_task)
    time.sleep(0.1)  # Allow some time for the task to execute
    loop.stop()
    loop_thread.join()
    
    assert task_executed, "Task was not executed"
    print("SyncEventLoop test passed")

if __name__ == "__main__":
    main()