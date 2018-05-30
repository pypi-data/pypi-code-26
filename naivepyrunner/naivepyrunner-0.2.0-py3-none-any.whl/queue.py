from collections import deque
from enum import Enum
from threading import Lock
from time import time
import heapq

class MetaQueue(type):
    def __call__(cls, mode=None, *args, **kwargs):
        if mode is None:
            mode = Queue.Mode.DUETIME

        queue = None
        if mode is Queue.Mode.DUETIME:
            queue = Queue.__new__(DuetimeQueue, *args, **kwargs)
        elif mode is Queue.Mode.MIN_DELAY:
            queue = Queue.__new__(TimeboxQueue, *args, **kwargs)
        else:
            queue = Queue.__new__(cls, *args, **kwargs)
        queue.__init__(*args, **kwargs)
        return queue

class Queue(object, metaclass=MetaQueue):
    class Mode(Enum):
        FIFO = 0,
        DUETIME = 1,
        MIN_DELAY = 2

    def __init__(self, *args, **kwargs):
        self.queue = deque()
        self.lock = Lock()

    def insert(self, job):
        with self.lock:
            self.queue.append(job)

    def is_first_due(self):
        with self.lock:
            if self.queue:
                return self.queue[0].is_due()
            return False

    def pop(self):
        try:
            return self.queue.popleft()
        except IndexError:
            return None

    def pop_if_due(self):
        with self.lock:
            if self.queue and self.queue[0].is_due():
                return self.queue.popleft()
        return None

class DuetimeQueue(Queue):#
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = []

    def insert(self, job):
        with self.lock:
            heapq.heappush(self.queue, (job.duetime, job))

    def pop(self):
        with self.lock:
            try:
                return heapq.heappop(self.queue)[1]
            except IndexError:
                return None

    def pop_if_due(self):
        with self.lock:
            if self.queue and self.queue[0][1].is_due():
                return heapq.heappop(self.queue)[1]
            return None

class TimeboxQueue(Queue):
    pass
