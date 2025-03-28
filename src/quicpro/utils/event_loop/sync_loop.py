"""
sync_loop.py - Synchronous event loop implementation.
This module implements a synchronous event loop using a ThreadPoolExecutor to schedule
tasks concurrently.
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from .base_loop import BaseEventLoop


class SyncEventLoop(BaseEventLoop):
    """
    A simple synchronous event loop that executes tasks using a thread pool.
    """

    def __init__(self, max_workers: int = 4) -> None:
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running = False
        self._lock = threading.Lock()
        self._tasks = []

    def schedule_task(self, func, *args, **kwargs):
        future = self.executor.submit(func, *args, **kwargs)
        with self._lock:
            self._tasks.append(future)
        return future

    def run_forever(self) -> None:
        self.running = True
        try:
            while self.running:
                with self._lock:
                    self._tasks = [t for t in self._tasks if not t.done()]
                time.sleep(0.01)
        finally:
            self.stop()

    def stop(self) -> None:
        self.running = False
        self.executor.shutdown(wait=True)
