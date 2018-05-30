from time import sleep
from threading import Thread

class QueueTransposer(Thread):
    def __init__(self, source, target, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = source
        self.target = target
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.transpose_all()
            sleep(0.1)

    def transpose_all(self):
        while self.running:
            element = self.source.pop()
            if not element:
                break
            self.target.insert(element)

    def transpose(self):
        element = self.source.pop()
        if element:
            self.target.insert(element)

    def stop(self):
        self.running = False
