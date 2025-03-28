"""
thread_pool.py - Simple thread pool wrapper.
This module provides a simple abstraction over ThreadPoolExecutor.
"""
from concurrent.futures import ThreadPoolExecutor


class ThreadPool:
    """
    A wrapper around ThreadPoolExecutor for submitting tasks.
    """

    def __init__(self, max_workers: int = 4) -> None:
        """
        Initialize the ThreadPool.
        Args:
            max_workers (int): Maximum number of worker threads.
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, func, *args, **kwargs):
        """
        Submit a task to the thread pool.
        Args:
            func: The callable to execute.
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        Returns:
            Future: A Future representing the submitted task.
        """
        return self.executor.submit(func, *args, **kwargs)

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the thread pool.
        Args:
            wait (bool): Wait for pending tasks to complete if True.
        """
        self.executor.shutdown(wait=wait)
