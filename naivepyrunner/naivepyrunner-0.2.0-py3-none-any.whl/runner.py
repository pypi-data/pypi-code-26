from time import sleep, time
from collections import deque
from enum import Enum
from threading import Thread

from .job import Job
from .task import Task
from .queue import Queue
from .queuetransposer import QueueTransposer
from .worker import Worker, DedicatedWorker

class MetaRunner(type):
    def __call__(cls, mode=None, *args, **kwargs):
        if mode is None:
            mode = Runner.Mode.SEQUENTIAL

        runner = None
        if mode is Runner.Mode.SHARED_QUEUE:
            runner = Runner.__new__(SharedQueueRunner, *args, **kwargs)
        elif mode == Runner.Mode.UNLIMITED:
            runner = Runner.__new__(UnlimitedRunner, *args, **kwargs)
        else:
            runner = Runner.__new__(SequentialRunner, *args, **kwargs)
        runner.__init__(*args, **kwargs)
        return runner

class Runner(object, metaclass=MetaRunner):
    class Mode(Enum):
        SEQUENTIAL = 0
        SHARED_QUEUE = 1
        UNLIMITED = 2

    def __init__(self, queue_mode=Queue.Mode.DUETIME, *args, **kwargs):
        self.queue = Queue(queue_mode)
        self.to_enqueue = Queue(Queue.Mode.FIFO)
        self.running = False

    def add_task(self, task):
        if not isinstance(task, Task):
            raise Exception('task is not a Task but a '+str(type(task)))
        job = Job(
            task = task,
            duetime = time()
        )
        self.queue.insert(job)

    def run(self):
        pass

    def stop(self):
        self.running = False

class SequentialRunner(Runner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_enqueue = None

    def run(self):
        self.running = True
        while self.running:
            job = self.queue.pop_if_due()

            if job and job.execute():
                self.queue.insert(job)

            if not job:
                sleep(0.01)

class SharedQueueRunner(Runner):
    def __init__(self, worker_pool_size=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not worker_pool_size:
            from multiprocessing import cpu_count
            worker_pool_size = cpu_count()

        self.tasks = Queue(Queue.Mode.FIFO)
        self.workers = [Worker(queue=self.queue, tasks=self.tasks)
            for i in range(worker_pool_size)
        ]
        self.transposer = QueueTransposer(source=self.tasks, target=self.queue)

    def run(self):
        self.running = True
        self.transposer.start()
        for worker in self.workers:
            Thread(target=worker.run).start()
        self.transposer.run()

    def stop(self):
        super().stop()
        for worker in self.workers:
            worker.stop()
            worker.join()
        self.transposer.stop()

class UnlimitedRunner(Runner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.to_enqueue = None
        self.queue = None
        self.threads = []

    def add_task(self, task):
        worker = DedicatedWorker(task)
        thread = Thread(target=worker.run)
        if self.running:
            thread.start()
        self.threads.append(thread)

    def run(self):
        self.running = True
        for thread in self.threads:
            thread.start()
        while self.running:
            sleep(0.1)

    def stop(self):
        for thread in self.threads:
            thread.join()
