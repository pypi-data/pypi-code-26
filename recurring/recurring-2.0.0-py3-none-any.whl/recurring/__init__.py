"""Simple library for running a callable every N seconds

job(callable, seconds) will call `callable` every `seconds` seconds in a dedicated thread that is destroyed on program exit, or on calling `job.terminate`.

Attempting to start or modify the rate of a job that has been terminated will raise a RuntimeError

Example:

    import recurring
    j = recurring.job(some_callable, some_seconds)
    j.start()
    # ...
    j.rate = some_new_seconds
    # ...
    j.stop()
    # ...
    j.start()
    # ...
    j.terminate()
"""

import threading
import time

from typing import Callable

class _Scheduler(threading.Thread):
    """Thread dedicated to calling `self.task` every `self.rate` seconds."""

    def __init__(self, rate: int, task: Callable) -> None:
        """Initialize our scheduling and calling thread.

        Args:
            rate (int): How often, in seconds, to schedule calls.
            task (Callable): What to call, must be of 0 arguments
        """
        super().__init__(daemon=True)
        self._rate = rate
        self._task = task
        self._state_changed = threading.Event()
        self._running = False
        self._alive = False

    @property
    def rate(self):
        """int: seconds in between calls."""
        return self._rate

    @rate.setter
    def rate(self, seconds):
        self._rate = seconds
        self._state_changed.set()

    def run(self):
        """Part of Thread's api, not intended to be called by users."""
        self._running = True
        self._alive = True

        while self._alive:
            if self._running:
                self._schedule()
            time.sleep(0.1)

    def _schedule(self):
        if self._state_changed.wait(self._rate):
            self._state_changed.clear()
        else:
            self._task()

    def resume(self):
        """Resume scheduled calling. Does nothing if we're already running."""
        self._running = True

    def stop(self):
        """Don't make or schedule any calls until further notice."""
        self._running = False
        self._state_changed.set()

    def terminate(self):
        """Exit out of our run() loop, permanently stop scheduling and making calls."""
        self._alive = False
        self._state_changed.set()


class job:
    """A job is something that is called repeatedly and the time to wait in between calls."""

    def __init__(self, func: Callable, rate: int) -> None:
        """Create a job.

        Args:
            func (Callable): What to call, a function of 0 arguments.
            rate (int): Seconds in between calls.
        """
        self._rate = rate
        self._func = func
        self._scheduler = _Scheduler(self._rate, self._func)
        self._terminated = False

    def start(self) -> None:
        """Start calling our regularly-scheduled function"""
        if self._terminated:
            raise RuntimeError('Attempt to start terminated job {}'.format(self))

        if self._scheduler.is_alive():
            self._scheduler.resume()
        else:
            self._scheduler.start()

    def stop(self) -> None:
        """Don't make any more calls until further notice"""
        self._scheduler.stop()

    def terminate(self) -> None:
        """Permanently stop making any more calls

        After this method has been called, attempts to start or change the rate of this job will raise a RuntimeError"""
        self._scheduler.terminate()
        self._terminated = True

        # ensure scheduler has cancelled out of it's run loop before returning
        # control to calling code
        while self._scheduler.is_alive():
            time.sleep(0.1)

    @property
    def rate(self) -> int:
        """int: seconds in between calls"""
        return self._rate

    @rate.setter
    def rate(self, seconds: int) -> None:
        if self._terminated:
            raise RuntimeError('Attempt to set the rate of terminated job {}'.format(self))

        self._rate = self._scheduler.rate = seconds

    def __str__(self):
        return f"{self.__class__.__qualname__}(rate={self._rate}, func={self._func})"
