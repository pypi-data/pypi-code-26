from time import sleep, time
from collections import deque
from queue import Queue

# For DedicatedWorker
from threading import Lock, Timer

from .task import Task

class Worker(object):
    def __init__(self, queue=None, tasks=None, *args, **kwargs):
        self.running = False
        self.queue = queue if queue else Queue()
        self.tasks = tasks if tasks else Queue()

    def run(self):
        self.running = True
        while self.running:
            if self.step():
                continue
            sleep(0.1)

    def step(self):
        job = self.queue.pop_if_due()
        if job and job.execute():
            self.tasks.insert(job)
        return bool(job)

    def stop(self):
        self.running = False

class DedicatedWorker(Worker):
    def __init__(self, task, *args, **kwargs):
        self.task = task
        self.running = False
        self.next_execution = time()

    def run(self):
        self.running = True
        while self.running:
            if self.next_execution <= time():
                if not self.step():
                    self.running = False
                    continue
            sleep(0.1)

    def step(self):
        sleep_time = self.task.execute()
        if sleep_time < 0:
            return False
        self.next_execution = time() + sleep_time
        return True

    def stop(self):
        self.running = False
        self.task.stop()
