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
import threading
from docker.errors import APIError, NotFound
from requests import HTTPError

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
        self._lock = threading.RLock()
        self._win_stop = False

        try:
            self._taskconfig = self._proxy.getTask(task_id)
        except HTTPError as e:
            if(e.response.status_code == 404):
                module_logger.warning('dhpc_task_{} existent on system but not on server'.format(task_id))
            else:
                module_logger.error('dpc_task_{} got error {} on server'.format(task_id, e.response.status_code))
            return

        module_logger.info('Initialized taskhandler with task id %s' % task_id)
        module_logger.debug('Initialized taskhandler with '+self.__repr__())

    def set_task_state(self, state):
        with self._lock:
            self._task.taskState = state

    def get_task_state(self):
        with self._lock:
            return self._task.taskState

    def stop_task(self):
        module_logger.info('ENTER stop_task: pausing task %s' % self._task.id)
        if(self._client.operatingSystem == 'WINDOWS'):
            module_logger.warning('Cannot pause containers... trying to stop them.')
            self.set_task_state('FAILED')
        elif(self._task.dockerImageType == 'WORKER'):
            self._task.stop_container()
            #self._task.remove_container()
        else:
            self._task.pause_container()

    def restart_task(self):
        module_logger.info('ENTER restart_task: restarting task %s' % self._task.id)
        self._task.unpause_container()

    def handle_task(self, restarted=False):

        def log(logger):
            loggers = self._proxy.getTaskOutputs(self._task.id)
            if (logger.id == None and (not restarted or len(loggers) == 0)):
                logger_json = self._proxy.postTaskOutput(logger)
                logger.id = logger_json['id']
            elif(logger.id == None and len(loggers) != 0):
                logger.id = loggers[-1]['id']
                self._proxy.patchTaskOutput(logger)
            else:
                self._proxy.patchTaskOutput(logger)

        module_logger.info('ENTER handle_task: Begin docker container initialization')
        self._task = task.Task(self._client, self._taskconfig)

        self._task.taskState = "RUNNING"

        try:
            gpu_slots = self._client.decrement_resources(self._task)
            self._task.gpuSlots = gpu_slots
        except ValueError as e:
            module_logger.warning("Task %s tried to allocate resources which were unavailable" % self._task.id)
            self._task.taskState = "SUBMITTED"
            self._client.del_taskhandler(self._task.id)
            self._proxy.putTask(self._task)
            return

        try:
            self._proxy.putTask(self._task)
        except HTTPError as e:
            if (e.response.status_code == 409):
                module_logger.debug("Increasing resources and throwing task away as another client was faster...")
                self._client.increment_resources(self._task)
                self._task.remove_container()
                self._client.del_taskhandler(self._task.id)
            else:
                raise e

        logger = tasklogger.TaskLogger(self._task)

        start_time = None
        if (not restarted):
            try:
                start_time = self._task.pull_and_run_image()
            except task.BindingError as e:
                module_logger.warning(e)
                logger.write(bytes(str(e), 'utf8'))
                log(logger)
                self._task.taskState = "SUBMITTED"
                self._proxy.putTask(self._task)
                self._client.increment_resources(self._task)
                self._client.del_taskhandler(self._task.id)
                # Cleanup failed containers
                self._task.reattach_container()
                self._task.remove_container()
                return
            except (TypeError, ValueError) as e:
                logger.write(bytes(str(e), 'utf8'))
                log(logger)
                self._task.taskState = "FAILED"
                self._proxy.putTask(self._task)
                self._client.increment_resources(self._task)
                self._client.del_taskhandler(self._task.id)
                # Cleanup failed containers
                self._task.reattach_container()
                self._task.remove_container()
                return
            except APIError as e:
                logger.write(bytes(str(e), 'utf8'))
                log(logger)
                self._task.taskState = "FAILED"
                self._proxy.putTask(self._task)
                self._client.increment_resources(self._task)
                self._client.del_taskhandler(self._task.id)
                # Cleanup failed containers
                self._task.reattach_container()
                self._task.remove_container()
                return
        else:
            self._task.reattach_container()
            self.restart_task()

        self._proxy.putTask(self._task)
        t = threading.Thread(target=self._task.monitor_container, args=(logger,),
                             name=('Task monitor for task %s' % self._task.id))
        t.start()

        time.sleep(5)

        timeExpired = lambda: self._task.dockerImageType == 'WORKER' and (int((time.time() - start_time)) > (self._task.durationMinutes * 60))

        try:
            while(not(timeExpired()) and (self._task.container_running() or not(logger.empty()))):
                log(logger)
                time.sleep(3)

        except NotFound as e:
            if(self._task.dockerImageType == 'WORKER'):
                self._task.taskState = "SUCCEEDED"
            else:
                self._task.taskState = "FAILED"

            self._client.increment_resources(self._task)
            self._proxy.putTask(self._task)
            return
        if(not timeExpired()):
            t.join()
        else:
            self._task.stop_container()

        self._client.increment_resources(self._task)

        if(self._client.operatingSystem == 'WINDOWS' and self.get_task_state() == 'FAILED'):
            # Windows containers are set to failed if they get paused
            pass
        else:
            self._task.taskState = 'SUCCEEDED'

        self._proxy.putTask(self._task)

        self._task.remove_container()
        self._client.del_taskhandler(self._task.id)
        module_logger.info('EXIT handle_task with code %s' % self._task.taskState)
        return





