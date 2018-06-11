from threading import Thread
from time import sleep

class EventListener():
  def __init__(self, event, handler, poll_interval, opts={}):
    self.filter = event.createFilter(fromBlock=1)
    self.poll_interval = poll_interval
    self.handler = handler

  def loop(self):
    while True:
      for event in self.filter.get_new_entries():
        self.handler(event)
      sleep(self.poll_interval)

  def run(self):
    self.worker = Thread(target=self.loop)
    self.worker.start()

  def stop(self):
    self.worker.join()