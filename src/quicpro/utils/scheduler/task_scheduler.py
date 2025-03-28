"""
Module for task scheduling.

Provides a TaskScheduler class for scheduling callables to be executed after a delay
using a provided event loop.
"""

import heapq
import time


class TaskScheduler:
    """
    Schedules tasks to run after specified delays using the event loop.
    """

    def __init__(self, event_loop) -> None:
        """
        Initialize the scheduler with a given event loop.

        Args:
            event_loop: An instance that provides a schedule_task() method.
        """
        self.event_loop = event_loop
        self.tasks = []

    def schedule(self, delay: float, func, *args, **kwargs) -> None:
        """
        Schedule a callable to run after the given delay.

        Args:
            delay (float): Delay in seconds.
            func: Callable to execute.
            *args: Positional arguments for callable.
            **kwargs: Keyword arguments for callable.
        """
        run_time = time.time() + delay
        heapq.heappush(self.tasks, (run_time, func, args, kwargs))

    def run_pending(self) -> None:
        """
        Execute all scheduled tasks whose run time has passed.
        """
        now = time.time()
        while self.tasks and self.tasks[0][0] <= now:
            _, func, args, kwargs = heapq.heappop(self.tasks)
            self.event_loop.schedule_task(func, *args, **kwargs)
