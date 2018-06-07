
import threading
import json
import logging

module_logger = logging.getLogger('DHPCLogger')

class TaskLogger(object):
    """Logger / Output collector for docker containers"""

    def __init__(self, task):

        module_logger.info('Initializing tasklogger for %s' % task.id)
        self._log = ''
        self._lock = threading.Lock()
        self._task = task
        self.output = ''
        self.id = None
        self.version = None


        module_logger.info('Initialized tasklogger for %s' % task.id)
        module_logger.debug('Initialized tasklogger with %s' % self.__repr__())

    def write(self, logs):
        module_logger.debug('ENTER write')
        self._lock.acquire()
        self._log += logs.decode('utf-8')
        self.output += self._log
        self._lock.release()

    def read(self):
        module_logger.debug('ENTER read')
        self._lock.acquire()
        logs = self._log
        self._log = ''
        self._lock.release()
        return logs

    def empty(self):
        return self._log == ''

    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        return {
            "content": self.output,
            "id": self.id,
            "task": self._task.json_repr(),
            "version": self.version
        }