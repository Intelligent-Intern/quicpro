# pylint: disable=duplicate-code
"""
Helper for executing a ThreadPool sample test.
"""
from concurrent.futures import ThreadPoolExecutor

def run_threadpool_sample(max_workers: int = 2, timeout: float = 1.0) -> bool:
    task_executed = False

    """Sample task to be executed in the thread pool."""
    def sample_task():
        nonlocal task_executed
        task_executed = True

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future = pool.submit(sample_task)
        future.result(timeout=timeout)
    return task_executed
