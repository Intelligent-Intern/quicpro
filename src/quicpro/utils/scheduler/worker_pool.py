"""
Worker pool module.
Provides a simple WorkerPool that submits tasks to an event loop.
"""


class WorkerPool:
    """
    A worker pool that submits tasks to the provided event loop.
    """

    def __init__(self, num_workers: int, event_loop) -> None:
        self.num_workers = num_workers
        self.event_loop = event_loop

    def submit(self, func, *args, **kwargs):
        """
        Submit a task to the event loop.
        Returns a Future.
        """
        return self.event_loop.schedule_task(func, *args, **kwargs)
