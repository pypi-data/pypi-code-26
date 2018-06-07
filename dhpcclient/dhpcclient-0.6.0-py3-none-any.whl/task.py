
import docker
import json
import logging
import time
import socket
from docker.errors import APIError, NotFound

module_logger = logging.getLogger('DHPCLogger')

CONTAINER_NAME_PREFIX = 'dhpc_task_%s'

class BindingError(Exception):
    pass

class TaskBaseDockerImage(object):
    """BaseDockerImage for a Task"""

    def __init__(self, baseDockerImage):
        if(baseDockerImage):
            self.id = baseDockerImage['id']
            self.url = baseDockerImage['url']
            self.dockerImageType = baseDockerImage['dockerImageType']
            self.version = baseDockerImage['version']
            self.isNone = False
        else:
            self.isNone = True
    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        if(self.isNone):
            return None

        return {
            'id': self.id,
            'url': self.url,
            'dockerImageType': self.dockerImageType,
            'version': self.version
        }

class Task(object):
    """Creates, manages and monitors docker containers."""

    def __init__(self, client, task_info):
        """
        Initiate the docker runner object
        #:param image_url: url of the docker image to pull
        :param client: The HPC Client used for object representation
        :param memory: Amount of memory to dedicate to this container in MB
        :param disk: Diskspace used by this container in MB
        :param runtime: Container runtime to use (runc, nvidia, ..)
        """

        module_logger.info('Initializing task with id %d' % task_info['id'])

        self._client = client
        self._docker = docker.from_env()
        self.dockerImageUrl = task_info['dockerImageUrl']
        self.durationMinutes = task_info['durationMinutes']
        self.externalPort = task_info['externalPort']
        self.internalPort = task_info['internalPort']
        self.id = task_info['id']
        self.baseDockerImage = TaskBaseDockerImage(task_info['baseDockerImage'])
        self.ioMountPathDst = task_info['ioMountPathDst']
        self.ioMountPathSrc = task_info['ioMountPathSrc']
        self.name = task_info['name']
        self.progress = task_info['progress']
        self.requiredCPUs = task_info['requiredCPUs']
        self.requiredGBDiskSpace = task_info['requiredGBDiskSpace']
        self.requiredGBRAM = task_info['requiredGBRAM']
        self.requiredGPUs = task_info['requiredGPUs']
        self.requiredOperatingSystem = task_info['requiredOperatingSystem']
        self.taskState = task_info['taskState']
        self.taskZip = task_info['taskZip']
        self.taskZipContentType = task_info['taskZipContentType']
        self.dockerImageType = task_info['dockerImageType']
        self.envVariables = task_info['envVariables']
        self.version = task_info['version']
        self.gpuSlots = ''
        self._container = None


        module_logger.info('Initialized task with id %s' % self.id)
        module_logger.debug('Initialized task with info '+self.__repr__())

    def _determine_runtime(self, gpuNo):
        module_logger.debug('ENTER _determine_runtime requiring %d GPUs and having %d GPUs ' % (gpuNo, self._client.availableGPUs))
        if(gpuNo > 0 and len(self._client.accessibleGPUs['nvidia']) > 0):
            module_logger.debug('EXIT _determine_runtime with nvidia')
            return 'nvidia'
        else:
            module_logger.debug('EXIT _determine_runtime with oci')
            return 'oci'

    def _create_path(self):
        module_logger.debug('ENTER _create_path...')

        if((self.ioMountPathSrc != None and self.ioMountPathDst != None) and
            (self.ioMountPathSrc != '' and self.ioMountPathDst != '')):
            module_logger.debug('EXIT _create_path, created path config')
            return {self.ioMountPathSrc: {'bind': self.ioMountPathDst, 'mode': 'rw'}}

        elif((self.ioMountPathSrc == None and self.ioMountPathDst == None) or
             (self.ioMountPathSrc == '' and self.ioMountPathDst == '')):
            module_logger.debug('EXIT _create_path, no path config available...')
            return {}

        else:
            module_logger.error('1 Mount Path is set the other is not. check your task config...')
            raise ValueError("IO Mount Path SRC or IO Mount Path DST is None but the other is not.")


    def _extract_port(self):
        module_logger.debug('ENTER _extract_port ...')

        if((self.internalPort == None or self.externalPort == None) and self.dockerImageType == 'WORKER'):
            raise TypeError("At least one port is not a number. Internal: %s, external %s" % (self.internalPort, self.externalPort))

        if(self.dockerImageType == 'WORKER'):
            internal_port = "%s/tcp" % self.internalPort
            try:
                external_port = int(self.externalPort)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    opened = sock.connect_ex(('localhost', external_port))

                if(opened == 0):
                    raise BindingError('Port {} already in use'.format(external_port))

                return {internal_port: external_port}
            except (TypeError) as e:
                module_logger.error('Could not extract external port with value %s' % self.internalPort)
                raise e
        elif(self.dockerImageType == 'WORKER'):
            module_logger.error('Could not extract internal port with value %s' % self.externalPort)
            raise TypeError
        else:
            return {}

    def _parse_envVars(self):
        module_logger.debug('ENTER _parse_envVars')
        if(self.envVariables != None):
            splitVars = self.envVariables.split(';')

            if(len(splitVars[0].split('=')) > 1):
                return splitVars
        return []

    def pull_and_run_image(self):
        """
        Creates the container and starts it.
        :param image_url: URL for the image to run
        :param command: command to run in the container
        """

        module_logger.info('ENTER pull_and_run_image: Starting Calculation of task %d' % self.id)


        kwargs = {'detach': True, 'mem_limit': str(self.requiredGBRAM) + 'g',
                  'name': 'dhpc_task_{}'.format(self.id),
                  'environment': []
                  }


        if (self._client.operatingSystem == 'WINDOWS'):
            # Windows does not support cpu_period and quota but number of cpus
            kwargs['cpu_count'] = self.requiredCPUs
        else:
            # Used as reference
            cpu_period = 100000
            cpu_quota = int(round(cpu_period * (self.requiredCPUs / self._client.totalCPUs)))

            module_logger.debug('cpu_quota = %d, cpu_period=%d' % (cpu_quota, cpu_period))

            kwargs['cpu_period'] = cpu_period
            kwargs['cpu_quota'] = cpu_quota


        kwargs['environment'] = self._parse_envVars()


        runtime = self._determine_runtime(self.requiredGPUs)
        if (runtime == 'nvidia'):
            kwargs['runtime'] = runtime
            kwargs['environment'].append('NVIDIA_VISIBLE_DEVICES={}'.format(self.gpuSlots))

        volumes = self._create_path()
        if(volumes != {}):
            kwargs['volumes'] = volumes

        if(self.dockerImageType == 'WORKER'):
            port = self._extract_port()
            module_logger.debug('Using port config ' + str(port))
            kwargs['ports'] = port

        module_logger.debug('Container arguments are '+str(kwargs))
        if(runtime == 'oci' and self.requiredGPUs > 0):
            # Some first steps for using opencl
            kwargs['device'] += "%s:'/dev/dri'" % self._client.accessibleGPUs['opencl'][0]
            module_logger.debug('Adding opencl device '+kwargs['device'])

        module_logger.info('Starting container... with image {}'.format(self.dockerImageUrl))
        self._container = self._docker.containers.run(self.dockerImageUrl, **kwargs)

        module_logger.debug('Started container task %s with image %s' % (self.id, self.dockerImageUrl))
        module_logger.debug('EXIT pull_and_run_image')

        return time.time()

    def monitor_container(self, logger):
        """
        Monitor the container constantly. This should be started in a separate thread
        :param logger: Where to write the fetched logs
        """

        module_logger.debug('ENTER monitor_container')
        for logline in self._container.logs(stream=True, stderr=True, stdout=True):
            logger.write(logline)

        module_logger.debug('EXIT monitor_container')
        return

    def reattach_container(self):
        module_logger.info('Reattaching container dhpc_task_{}'.format(self.id))
        self._container = self._docker.containers.get('dhpc_task_{}'.format(self.id))

    def remove_container(self):
        module_logger.info('ENTER remove_container, removing container of task %s' % self.id)
        try:
            self._container.remove()
        except APIError as e:
            pass

    def pause_container(self):
        module_logger.debug('ENTER pause_container, pausing container of task %s' % self.id)
        try:
            self._container.pause()
        except APIError as e:
            if('already paused' in str(e)):
                return
            elif('not running' in str(e)):
                return
            else:
                raise e

    def unpause_container(self):
        module_logger.debug('ENTER unpause_container, unpause container of task %s' % self.id)
        self._container.unpause()

    def stop_container(self):
        module_logger.info('ENTER stop_container, stopping container of task %s' % self.id)
        if(self._container != None):
            self._container.stop()

    def container_running(self):
        module_logger.debug('ENTER container_running of container belonging to task %s' % self.id)
        self._container.reload()

        return self._container.status in ['running', 'restarting', 'created']

    def __repr__(self):
        return json.dumps(self.json_repr())

    def json_repr(self):
        return {
            "client": self._client.json_repr(),
            "baseDockerImage": self.baseDockerImage.json_repr(),
            "dockerImageUrl": self.dockerImageUrl,
            "dockerImageType": self.dockerImageType,
            "durationMinutes": self.durationMinutes,
            "externalPort": self.externalPort,
            "internalPort": self.internalPort,
            "id": self.id,
            "ioMountPathDst": self.ioMountPathDst,
            "ioMountPathSrc": self.ioMountPathSrc,
            "name": self.name,
            "progress": self.progress,
            "requiredCPUs": self.requiredCPUs,
            "requiredGBDiskSpace": self.requiredGBDiskSpace,
            "requiredGBRAM": self.requiredGBRAM,
            "requiredGPUs": self.requiredGPUs,
            "taskState": self.taskState,
            "taskZip": self.taskZip,
            "taskZipContentType": self.taskZipContentType,
            "requiredOperatingSystem": self.requiredOperatingSystem,
            "version": self.version,
            "envVariables": self.envVariables
        }
