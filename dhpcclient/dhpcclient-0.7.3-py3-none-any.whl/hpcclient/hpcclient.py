#!/usr/bin/env python3

import os
import sys

dirname = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, dirname)
import configparser
import psutil
import time
import threading
import requestproxy
import taskhandler
import socket
import platform
import json
import logging
from requests import HTTPError

CONFIG_PATH = dirname + '/etc'

# I know this is ULTRA ugly :) - But needed for cross-platform work
if(platform.uname()[0].upper() != 'WINDOWS'):
    from service import Service
else:
    Service = object


module_logger = logging.getLogger('DHPCLogger')


class HPCClient(Service):
    """
        Manages the client side of the distributed HPC
    """

    def __init__(self, daemonize, *args, **kwargs):
        """
            Collects the HW-information, instantiates the connector and so on.
        """

		# Only on Linux (Or say, daemonized)
        if(daemonize):
            super(HPCClient, self).__init__(*args, **kwargs)
        
        self.daemonize = daemonize

        cfg = self._load_config()
        _logpath = self._get_logpath(cfg)

        self.logger = HPCClient.init_logger(_logpath)

        module_logger.info('Initializing HPCClient...')
        self._lock = threading.Lock()
        self.availableCPUs = psutil.cpu_count()
        self.availableGBRAM = int(round(psutil.virtual_memory()[0] / 1024 / 1024 / 1024))

        nvGpuNo, nvGpuDevs = self._get_nvgpus()
        self.availableGPUs = nvGpuNo
        self.accessibleGPUs = {'nvidia': nvGpuDevs, 'amd': []}

        self.availableGBDiskSpace = int(round(self._get_disk_space()))
        self.dateLastRequest = time.strftime('%Y-%m-%d', time.localtime())
        self.ipAddress = socket.gethostbyname(socket.gethostname())
        self.operatingSystem = self._get_uname().upper()
        self.id = None

        self._proxy = self._init_conn_settings(cfg)
        self._set_server(cfg)
        self._set_first_request(cfg)
        self._set_id(cfg)
        self._set_interval(cfg)
        self._set_max_image_age(cfg)
        self._save_config(cfg)

        self._taskHandlers = {}

        module_logger.info('Initialized HPCClient...')
        module_logger.debug('Initialized HPCClient with configuration '+self.__repr__())

    @staticmethod
    def init_logger(logpath):
        app_logger = logging.getLogger('DHPCLogger')
        app_logger.setLevel(logging.DEBUG)
        fh_logger = logging.FileHandler(logpath + '/dhpc.log')
        fh_logger.setLevel(logging.DEBUG)
        cons_logger = logging.StreamHandler()
        cons_logger.setLevel(logging.WARNING)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        fh_logger.setFormatter(formatter)
        cons_logger.setFormatter(formatter)

        app_logger.addHandler(fh_logger)
        app_logger.addHandler(cons_logger)
        return app_logger

    def _get_clgpus(self):
        gpu_count = 0

        import amd
        try:
            gpu_count = int(amd.query_clinfo())
        except:
            pass

        return gpu_count

    def _get_nvgpus(self):
        gpu_count = 0
        gpu_devs = []
        import nvidia
        try:
            gpu_count = int(nvidia.query_nvsmi('count')[0][0])
            gpu_devs = list(map(lambda x: x[0], nvidia.query_nvsmi('name')))
        except:
            pass

        return gpu_count, gpu_devs


    def _init_conn_settings(self, cfg):
        module_logger.debug('ENTER _init_conn_settings: '+str(cfg))
        rqp = requestproxy.RequestProxy('http://' + cfg['common']['server'] + '/api')
        module_logger.debug('EXIT _init_conn_settings: '+rqp.__repr__())
        return rqp

    def _set_interval(self, cfg):
        module_logger.debug('ENTER _set_interval: '+str(cfg))
        try:
            self._interval = int(cfg['client']['interval'])
            module_logger.debug('using poll interval %d' % self._interval)
        except KeyError:
            module_logger.info('No polling interval set. Using default = 30s ...')
            self._interval = 30
        module_logger.debug('EXIT _set_interval')

    def _get_logpath(self, cfg):
        try:
            logpath = cfg['client']['logdir']
        except KeyError:
            return '/var/tmp'

        return logpath

    def _set_max_image_age(self, cfg):
        module_logger.debug('ENTER _set_image_age: ' + str(cfg))
        try:
            self._max_image_age = int(cfg['client']['max_image_age'])
            module_logger.debug('using image max age %s ' % self._max_image_age)
        except KeyError:
            module_logger.info('No image max age set. Using default = 30 days ...')
            self._max_image_age = 30
        module_logger.debug('EXIT _set_image_age')

    def _set_id(self, cfg):
        module_logger.debug('ENTER _set_id: ' + str(cfg))
        try:
            self.id = cfg['client']['id']
            module_logger.debug('client id (=%s) found so using it... ' % self.id)
        except KeyError:
            module_logger.debug('No client id found, registering system...')
            # Register client
            json_client = self._proxy.postClient(self)
            self.id = json_client['id']
            module_logger.debug('Client id received is %s ' % self.id)

            if(self.id != None):
                cfg['client']['id'] = str(self.id)

        module_logger.debug('EXIT _set_id')

    def _set_server(self, cfg):
        module_logger.debug('ENTER _set_server: ' + str(cfg))
        try:
            self.server = cfg['common']['server']
            module_logger.debug('remote server is %s ' % self.server)
        except KeyError:
            print("No server configured. add 'server=<IP>' to config.ini in [common] section. Exiting...")
            module_logger.error('No server configured. Exiting...' % self.server)
            sys.exit(1)

    def _set_first_request(self, cfg):
        module_logger.debug('ENTER _set_first_request: ' + str(cfg))
        try:
            self.dateFirstRequest = cfg['client']['dateFirstRequest']
        except KeyError:
            self.dateFirstRequest = time.strftime('%Y-%m-%d', time.localtime())

        module_logger.debug('EXIT _set_first_request')

    def _get_uname(self):
        module_logger.debug('ENTER _get_uname')
        uname = platform.uname()
        module_logger.debug('EXIT _get_uname with uname=%s' % uname[0])
        return uname[0]

    def _get_disk_space(self):
        module_logger.debug('ENTER _get_disk_space')
        disk_parts = psutil.disk_partitions()
        disk_space = psutil.disk_usage(disk_parts[0].mountpoint).free / 1024 / 1024 / 1024
        module_logger.debug('EXIT _get_disk_space with disk_space=%f' % disk_space)
        return disk_space

    def _load_config(self):
        """
            Parse configuration
            :return: configuration values
        """
        cp = configparser.ConfigParser()
        cp.read(CONFIG_PATH+'/config.ini')
        return cp

    def _save_config(self, cfg):
        module_logger.debug('ENTER _save_config')
        with open(CONFIG_PATH+'/config.ini', 'w') as cfg_file:
            cfg.write(cfg_file)

        module_logger.debug('EXIT _save_config')

    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        return {
            "availableCPUs": self.availableCPUs,
            "availableGBDiskSpace": self.availableGBDiskSpace,
            "availableGBRAM": self.availableGBRAM,
            "availableGPUs": self.availableGPUs,
            "dateFirstRequest": self.dateFirstRequest,
            "dateLastRequest": self.dateLastRequest,
            "id": self.id,
            "ipAddress": self.ipAddress,
            "operatingSystem": self.operatingSystem
        }

    def activate(self):
        module_logger.debug('ENTER activate.. Activating all containers')
        for task_id in self._taskHandlers:
            th = self._taskHandlers[task_id]
            th.restart_task()

        self.terminate(True)
        module_logger.debug('EXIT activate.. Activated all containers')
    def deactivate(self):
        module_logger.debug('ENTER deactivate.. deactivating all containers')
        for task_id in self._taskHandlers:
            th = self._taskHandlers[task_id]
            th.stop_task()
        self.terminate(False)
        module_logger.debug('EXIT deactivate.. deactivated all containers')

    def terminate(self, term):
        pass   

    def increment_resources(self, task):
        module_logger.info('Task %s is releasing resources' % task.id)
        self._lock.acquire()
        self.availableGPUs += task.requiredGPUs
        self.availableGBRAM += task.requiredGBRAM
        self.availableGBDiskSpace += task.requiredGBDiskSpace
        self.availableCPUs += task.requiredCPUs
        self._lock.release()

    def decrement_resources(self, task):
        module_logger.info('Task %s is acquiring resources' % task.id)
        self._lock.acquire()
        if((self.availableGPUs - task.requiredGPUs) < 0 or
        (self.availableGBRAM - task.requiredGBRAM) < 0 or
        (self.availableGBDiskSpace - task.requiredGBDiskSpace) < 0 or
        (self.availableCPUs - task.requiredCPUs) < 0):
            raise ValueError("This task needs to much resources, returning ...")

        self.availableGPUs -= task.requiredGPUs
        self.availableGBRAM -= task.requiredGBRAM
        self.availableGBDiskSpace -= task.requiredGBDiskSpace
        self.availableCPUs -= task.requiredCPUs
        self._lock.release()

    def run(self):
        module_logger.debug('ENTER hpcclient.run...')

        task_filter = "?availableCPUs=%s&availableGBDiskSpace=%s&availableGBRAM=%s&availableGPUs=%s&operatingSystem=%s&taskState=SUBMITTED"
				
        if(self.daemonize):
            terminate = self.got_sigterm
            self.activate()
        else:
            terminate = lambda: False
						
				
        while(not(terminate())):
            task_filter_request = task_filter % (self.availableCPUs, self.availableGBDiskSpace, self.availableGBRAM,
                                         self.availableGPUs, self.operatingSystem)

            module_logger.debug('task_filter_request is '+task_filter_request)


            try:
                queried_tasks = self._proxy.getTasks(filter=task_filter_request)

                module_logger.info('tasks available for this client are ' + str(json.dumps(queried_tasks)))

                for task in queried_tasks:
                    if (task['id'] not in self._taskHandlers.keys()):
                        new_task = taskhandler.TaskHandler(self, self._proxy, task['id'])
                        self._taskHandlers[task['id']] = new_task
                        t = threading.Thread(target=new_task.handle_task, name='Taskhandler Task ID %s' % task['id'])
                        t.start()

            except HTTPError as e:
                print('HTTPError status %s thrown because of %s ' % (e.response.status_code, e.response.reason))

            time.sleep(self._interval)
						
        if(self.daemonize):
            self.deactivate()

if (__name__ == '__main__'):
    import sys

    if(platform.uname()[0].upper() == 'WINDOWS'):
        sys.exit("Daemon mode only supported on Linux")

    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()

    if(not(os.path.exists('/tmp/run'))):
        os.mkdir('/tmp/run', mode=0o0755)

    service = HPCClient(True, 'hpcclient', pid_dir='/tmp/run')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)
