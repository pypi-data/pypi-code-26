
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
        #self.output = ''
        self.id = None
        self.version = None


        module_logger.info('Initialized tasklogger for %s' % task.id)
        module_logger.debug('Initialized tasklogger with %s' % self.__repr__())

    def write(self, logs):
        module_logger.debug('ENTER write')
        with self._lock:
            self._log += logs.decode('utf-8')
            #self.output += self._log

    def read(self):
        module_logger.debug('ENTER read')
        with self._lock:
            logs = self._log
            self._log = ''
            return logs

    def empty(self):
        with self._lock:
            return self._log == ''

    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        with self._lock:
            return {
                "content": self._log,
                "id": self.id,
                "task": self._task.json_repr(),
                "version": self.version
            }