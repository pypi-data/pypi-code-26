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
from dns import resolver, exception
import logging
import docker
import re
from shutil import copyfile
from requests import HTTPError, ConnectionError

DEFAULT_CONFIG_PATH = dirname + '/etc'
DEFAULT_LOGPATH = '/var/tmp'
DEFAULT_LOGLEVEL = 'INFO'
DEFAULT_INTERVAL = 300 # 300 Sec = 5min
DEFAULT_KEEP_MAX = 7 # 7 Days
DEFAULT_ID = None
DEFAULT_CLEANUP_TIME = 5 # 5 AM (Time)

# I know this is ULTRA ugly :) - But needed for cross-platform work as Service is only usable for Linux platforms
pltform = platform.uname()[0]
if(pltform.upper() != 'WINDOWS'):
    if(not os.path.exists(dirname + '/etc/config.ini')):
        copyfile(dirname+'/share/config_linux.ini', dirname+'/etc/config.ini')
    from service import Service
else:
    if (not os.path.exists(dirname + '/etc/config.ini')):
        copyfile(dirname + '/share/config_windows.ini', dirname + '/etc/config.ini')
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

        cfg = self._load_config()
        _logpath = self._get_config_value(cfg, 'client', 'logdir', DEFAULT_LOGPATH)
        _loglevel = self._get_config_value(cfg, 'client', 'loglevel', DEFAULT_LOGLEVEL)

        self.logger = HPCClient.init_logger(_logpath, _loglevel)
        self.version = None

        module_logger.info('Initializing HPCClient...')

        # Daemon initialization
        self._deactivated = False
        self._should_terminate = False
        self.daemonize = daemonize
        self._cleanup = False

        # Config file values (or default)
        self._interval = int(self._get_config_value(cfg, 'client', 'interval', DEFAULT_INTERVAL))
        self._keep_max = int(self._get_config_value(cfg, 'client', 'keep_max', DEFAULT_KEEP_MAX))
        self._cleanup_time = int(self._get_config_value(cfg, 'client', 'cleanup_time', DEFAULT_CLEANUP_TIME))

        self.server = self._get_config_value(cfg, 'common', 'server', 'localhost')
        _user = self._get_config_value(cfg, 'common', 'user', None)
        _passwd = self._get_config_value(cfg, 'common', 'passwd', None)
        self.id = self._get_config_value(cfg, 'client', 'id', DEFAULT_ID)

        self._taskHandlers = {}
        self._lock = threading.Lock()
        self._taskhandler_lock = threading.RLock()

        self.totalCPUs = psutil.cpu_count()

        # Values that are sent to the server except ID and version
        self.dateFirstRequest = self._get_config_value(cfg, 'client', 'dateFirstRequest',
                                                       time.strftime('%Y-%m-%d', time.localtime()))
        self.availableCPUs = self.totalCPUs
        self.availableGBRAM = int(round(psutil.virtual_memory()[0] / 1024 / 1024 / 1024))

        nvGpuNo, nvGpuDevs = self._get_nvgpus()
        self.availableGPUs = nvGpuNo
        self.accessibleGPUs = {'nvidia': nvGpuDevs, 'amd': []}
        self.availableGBDiskSpace = int(round(self._get_disk_space()))
        self.dateLastRequest = time.strftime('%Y-%m-%d', time.localtime())

        try:
            self.ipAddress = resolver.query(socket.getfqdn())[0].address
        except (resolver.NoAnswer, resolver.NXDOMAIN, exception.Timeout):
            self.ipAddress = socket.gethostbyname(socket.getfqdn())

        self.operatingSystem = docker.from_env().version()['Os'].upper()


        # Proxy init
        self._proxy = requestproxy.RequestProxy(self.server, _user, _passwd)
        _user, _passwd = None, None

        if (self.id == None):
            # Register client
            client_json = self._proxy.postClient(self)
            self.id = client_json['id']
            cfg['client']['id'] = str(self.id)

        client_json = self._proxy.getClient(self.id)
        self.version = client_json['version']

        self._save_config(cfg)
        module_logger.info('Initialized HPCClient...')
        module_logger.debug('Initialized HPCClient with configuration '+self.__repr__())
        module_logger.debug('Having {} nvidia GPUs and {} AMD GPUs available'.format(self.accessibleGPUs['nvidia'],
                                                                                     self.accessibleGPUs['amd']))
    @staticmethod
    def init_logger(logpath, loglevel):
        app_logger = logging.getLogger('DHPCLogger')
        app_logger.setLevel(loglevel.upper())
        fh_logger = logging.FileHandler(logpath + '/dhpc.log')
        fh_logger.setLevel(loglevel.upper())
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
            gpu_devs = list(map(lambda x: [x[0], False], nvidia.query_nvsmi('name')))
        except:
            pass

        return gpu_count, gpu_devs

    def _get_config_value(self, cfg, section, subsection, default_value):
        try:
            return cfg[section][subsection]
        except KeyError as e:
            module_logger.debug('Key {} not found, using default {}'.format(subsection, default_value))
            cfg[section][subsection] = str(default_value)
            return default_value

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
        cp.read(DEFAULT_CONFIG_PATH+'/config.ini')

        return cp

    def _save_config(self, cfg):
        module_logger.debug('ENTER _save_config')
        with open(DEFAULT_CONFIG_PATH+'/config.ini', 'w') as cfg_file:
            cfg.write(cfg_file)

        module_logger.debug('EXIT _save_config')

    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        with self._lock:
            return {
                "availableCPUs": self.availableCPUs,
                "availableGBDiskSpace": self.availableGBDiskSpace,
                "availableGBRAM": self.availableGBRAM,
                "availableGPUs": self.availableGPUs,
                "dateFirstRequest": self.dateFirstRequest,
                "dateLastRequest": self.dateLastRequest,
                "id": self.id,
                "ipAddress": self.ipAddress,
                "operatingSystem": self.operatingSystem,
                "version": self.version
            }

    def activate(self):
        module_logger.debug('ENTER activate.. Activating all containers')

        with self._taskhandler_lock:
            for task_id in self._taskHandlers:
                th = self._taskHandlers[str(task_id)]
                th.restart_task()

        self._deactivated = False
        module_logger.debug('EXIT activate.. Activated all containers')

    def deactivate(self):
        module_logger.debug('ENTER deactivate.. deactivating all containers')
        with self._taskhandler_lock:
            for task_id in self._taskHandlers:
                th = self._taskHandlers[str(task_id)]
                th.stop_task()

        self._deactivated = True
        module_logger.debug('EXIT deactivate.. deactivated all containers')

    def _reinitialize_taskhandlers(self):
        module_logger.debug('ENTER reinitialize_taskhandlers')
        client = docker.from_env()
        cntnrs = client.containers.list(filters={'status': 'paused'})
        cntnrs = list(filter(lambda c: re.match('dhpc_task_', c.name), cntnrs))

        module_logger.info('Found {} containers to reinitialize'.format(str(cntnrs)))

        for cntnr in cntnrs:
            id = cntnr.name.split('_')[-1]
            if(id.isnumeric()):
                self.create_and_run_taskhandler(id, restarted=True)

        module_logger.debug('EXIT reinitialize_taskhandlers')

    def terminate(self, term):
        module_logger.debug('ENTER terminate')
        with self._lock:
            self._should_terminate = term

    def _should_term(self):
        with self._lock:
            return self._should_terminate


    def _reserve_gpus(self, count, vendor):
        module_logger.debug('ENTER _reserve_gpus: {} GPUs needed'.format(count))
        gpus = self.accessibleGPUs[vendor]
        idxes = []
        for idx, gpu in enumerate(gpus):
            if(not gpu[1] and count > 0):
                self.accessibleGPUs[vendor][idx][1] = True
                idxes.append(str(idx))
                count -= 1
        module_logger.debug('EXIT _release_gpus, reserved {}'.format(idxes))

        return ','.join(idxes)

    def _release_gpus(self, count, vendor):
        module_logger.debug('ENTER _release_gpus, releasing {} GPUs {}'.format(vendor, count))
        idxes = []
        if (count != None and count != ''):
            idxes = list(map(lambda s: int(s), count.split(',')))
            if (len(idxes) > 0):
                for idx in idxes:
                    self.accessibleGPUs[vendor][idx][1] = False
        module_logger.debug('EXIT _release_gpus, released {}'.format(idxes))


    def increment_resources(self, task):
        module_logger.info('Task %s is releasing resources' % task.id)
        with self._lock:
            self.availableGPUs += task.requiredGPUs
            self.availableGBRAM += task.requiredGBRAM
            self.availableGBDiskSpace += task.requiredGBDiskSpace
            self.availableCPUs += task.requiredCPUs
            self._release_gpus(task.gpuSlots, 'nvidia')

    def decrement_resources(self, task):
        module_logger.info('Task %s is acquiring resources' % task.id)

        with self._lock:
            if((self.availableGPUs - task.requiredGPUs) < 0 or
            (self.availableGBRAM - task.requiredGBRAM) < 0 or
            (self.availableGBDiskSpace - task.requiredGBDiskSpace) < 0 or
            (self.availableCPUs - task.requiredCPUs) < 0):
                raise ValueError("This task needs to much resources, returning ...")

            self.availableGPUs -= task.requiredGPUs
            self.availableGBRAM -= task.requiredGBRAM
            self.availableGBDiskSpace -= task.requiredGBDiskSpace
            self.availableCPUs -= task.requiredCPUs

            gpu_slots = self._reserve_gpus(task.requiredGPUs, 'nvidia')

            return gpu_slots

    def add_taskhandler(self, task_id, task_handler):
        module_logger.debug('Adding Task %s to taskhandler dict' % task_id)
        with self._taskhandler_lock:
            self._taskHandlers[str(task_id)] = task_handler

    def del_taskhandler(self, task_id):
        module_logger.debug('Removing Task %s from taskhandler dict' % task_id)
        with self._taskhandler_lock:
            del self._taskHandlers[str(task_id)]

    def create_and_run_taskhandler(self, id, restarted=False):
        if(id not in self._taskHandlers):
            new_task = taskhandler.TaskHandler(self, self._proxy, id)
            self.add_taskhandler(id, new_task)
            t = threading.Thread(target=new_task.handle_task, name='Taskhandler Task ID %s' % id, args=(restarted,))
            t.start()

    def _do_cleanup(self):
        module_logger.info('Will now start cleanup')
        def keep_expired(docker_date):
            docker_tm_day = time.strptime(docker_date.split('T')[0], "%Y-%m-%d")[7] # 7 = Day of the year in struct
            now_tm_day = time.struct_time(time.localtime())[7] # 7 = day of the year in struct
            return (now_tm_day - docker_tm_day) > self._keep_max

        client = docker.from_env()
        cntnrs = client.containers.list(all=True, filters={'status': 'exited'})
        cntnrs = list(filter(lambda c: 'dhpc_task' in c.name and keep_expired(c.attrs['State']['FinishedAt']), cntnrs))
        images = [c.image for c in cntnrs]

        for c in cntnrs:
            module_logger.debug('Removing container {}'.format(c.name))
            c.remove()
        for i in images:
            module_logger.debug('Removing image {} tag {}'.format(i.id, i.tag))
            client.images.remove(i.id)
        module_logger.info('Cleanup done')

    def _set_cleanup_state(self, state):
        with self._lock:
            self._cleanup = state

    def _get_cleanup_state(self):
        with self._lock:
            return self._cleanup

    def _handle_cleanup(self):
        module_logger.debug('Entering handle_cleanup')
        hour = int(time.strftime('%H', time.localtime()))
        if(hour >= self._cleanup_time and hour < self._cleanup_time + 1):
            module_logger.info('Cleanup of old docker containers and task images initialized')
            timed_cleanup = threading.Timer(3600., self._do_cleanup) #Wait 1 hour before cleanup
            timed_cleanup.start()
            self._set_cleanup_state(True)
            timed_cleanup.join()
            self._set_cleanup_state(False)


    def run(self):
        module_logger.debug('ENTER hpcclient.run...')

        task_filter = "?availableCPUs=%s&availableGBDiskSpace=%s&availableGBRAM=%s&availableGPUs=%s&operatingSystem=%s&taskState=SUBMITTED"

        term = False
        if(self.daemonize):
            term = self.got_sigterm()
        else:
            term = False
        self.terminate(term)

        module_logger.debug('should terminate {}'.format(self._should_term()))

        self._reinitialize_taskhandlers()

        while(not(self._should_term())):
            if(not self._get_cleanup_state()):
                threading.Thread(name='Cleanup-Thread', target=self._handle_cleanup).start()

            if(not self._deactivated):
                with self._lock:
                    self.availableGBDiskSpace = int(round(self._get_disk_space()))

                    task_filter_request = task_filter % (self.availableCPUs, self.availableGBDiskSpace, self.availableGBRAM,
                                                         self.availableGPUs, self.operatingSystem)

                module_logger.debug('task_filter_request is '+task_filter_request)

                try:
                    queried_tasks = self._proxy.getTasks(filter=task_filter_request)
                    module_logger.debug('tasks available for this client are ' + str(json.dumps(queried_tasks)))

                    if(len(queried_tasks) > 0):
                        self.create_and_run_taskhandler(queried_tasks[0]['id'])

                except ConnectionError as e:
                    print('new Connection Error thrown')
                    module_logger.warning('NewConnectionError thrown in')
                except HTTPError as e:
                    print('HTTPError status %s thrown because of %s ' % (e.response.status_code, e.response.reason))
                except BaseException as e:
                    module_logger.error('Unhandled Exception {} thrown'.format(str(e)))

                time.sleep(self._interval)

                if(self.daemonize):
                    self.terminate(self.got_sigterm())
                    module_logger.info('got_sigterm is {}'.format(self.got_sigterm()))

                module_logger.debug('should_terminate is {}'.format(self._should_term()))
            else:
                time.sleep(self._interval)

        module_logger.info('shutting down containers...')
        self.deactivate()

def main():
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

if (__name__ == '__main__'):
    main()
