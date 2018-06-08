
import os
import sys
import threading
import time

dirname = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, dirname)

import requestproxy
import tasklogger
import task
import logging
from docker.errors import APIError

module_logger = logging.getLogger('DHPCLogger')

class TaskHandler(object):
    """
        Handles tasks and sends task states to server
    """

    def __init__(self, client, proxy, task_id):
        """
            Taskhandler init
        """


        module_logger.info('Initializing taskhandler with task id %s' % task_id)
        self._proxy = proxy
        self._client = client
        self._taskconfig = self._proxy.getTask(task_id)
        module_logger.info('Initialized taskhandler with task id %s' % task_id)
        module_logger.debug('Initialized taskhandler with '+self.__repr__())

    def stop_task(self):
        module_logger.info('ENTER stop_task: pausing task %s' % self._task.id)
        self._task.pause_container()

    def restart_task(self):
        module_logger.info('ENTER restart_task: restarting task %s' % self._task.id)
        self._task.unpause_container()

    def handle_task(self):

        def log(logger):
            if (logger.id == None):
                logger_json = self._proxy.postTaskOutput(logger)
                logger.id = logger_json['id']
            else:
                self._proxy.patchTaskOutput(logger)

        module_logger.info('ENTER handle_task: Begin docker container initialization')
        self._task = task.Task(self._client, self._taskconfig)

        self._task.taskState = "RUNNING"

        try:
            self._client.decrement_resources(self._task)
        except ValueError as e:
            module_logger.warning("Task %s tried to allocate resources which were unavailable" % task.id)
            self._task.taskState = "SUBMITTED"
            return
        finally:
            self._proxy.putTask(self._task)


        logger = tasklogger.TaskLogger(self._task)
        start_time = None
        try:
            start_time = self._task.pull_and_run_image()
        except (TypeError, ValueError) as e:
            logger.write(e)
            log(logger)
            self._task.taskState = "FAILED"
            self._proxy.putTask(self._task)
            self._client.increment_resources(self._task)
            return
        except APIError as e:
            logger.write(bytes(str(e), 'utf8'))
            log(logger)
            self._task.taskState = "FAILED"
            self._proxy.putTask(self._task)
            self._client.increment_resources(self._task)
            return

        self._proxy.putTask(self._task)
        t = threading.Thread(target=self._task.monitor_container, args=(logger,),
                             name=('Task manager for task %s' % self._task.id))
        t.start()

        time.sleep(5)

        timeExpired = lambda: (int((time.time() - start_time)) > (self._task.durationMinutes * 60)) and self._task.dockerImageType == 'WORKER'

        while(not(timeExpired()) and (self._task.container_running() or not(logger.empty()))):
            log(logger)
            time.sleep(3)

        if(not timeExpired()):
            t.join()
        else:
            self._task.stop_container()

        self._client.increment_resources(self._task)
        self._task.taskState = "SUCCEEDED"
        self._proxy.putTask(self._task)

        self._task.remove_container()

        module_logger.info('EXIT handle_task with code %s' % self._task.taskState)
        return





