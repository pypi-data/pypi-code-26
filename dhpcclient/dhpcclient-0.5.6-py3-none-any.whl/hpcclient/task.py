
import docker
import json
import logging
import time

module_logger = logging.getLogger('DHPCLogger')

CONTAINER_NAME_PREFIX = 'dhpc_task_%s'

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

        CONTAINER_NAME_PREFIX = 'dhpc_task_'
        module_logger.info('Initializing task with id %d' % task_info['id'])

        self._client = client
        self._docker = docker.from_env()
        self.dockerImageUrl = task_info['dockerImageUrl']
        self.durationMinutes = task_info['durationMinutes']
        self.externalPort = task_info['externalPort']
        self.internalPort = task_info['internalPort']
        self.id = task_info['id']
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


        module_logger.info('Initialized task with id %s' % self.id)
        module_logger.debug('Initialized task with info '+self.__repr__())

    def _determine_runtime(self, gpuNo):
        module_logger.debug('ENTER _determine_runtime requiring %d GPUs and having %d GPUs ' % (gpuNo, self._client.availableGPUs))
        if(gpuNo > 0 and 'nvidia' in self._client.accessibleGPUs.keys()):
            module_logger.debug('EXIT _determine_runtime with nvidia')
            return 'nvidia'
        else:
            module_logger.debug('EXIT _determine_runtime with oci')
            return 'oci'

    def _create_path(self):
        module_logger.debug('ENTER _create_path...')
        if(self.ioMountPathSrc != None and self.ioMountPathDst != None):
            module_logger.debug('EXIT _create_path, created path config')
            return { self.ioMountPathSrc: {'bind': self.ioMountPathDst, 'mode': 'rw'} }
        elif(self.ioMountPathSrc == None and self.ioMountPathDst == None):
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
                return {internal_port: external_port}
            except (TypeError) as e:
                module_logger.error('Could not extract external port with value %s' % self.internalPort)
                raise e
        elif(self.dockerImageType == 'WORKER'):
            module_logger.error('Could not extract internal port with value %s' % self.externalPort)
            raise TypeError
        else:
            return {}


    def pull_and_run_image(self):
        """
        Creates the container and starts it.
        :param image_url: URL for the image to run
        :param command: command to run in the container
        """

        module_logger.info('ENTER pull_and_run_image: Starting Calculation of task %d' % self.id)
        # Used as reference
        cpu_period = 100000
        cpu_quota = int(round(cpu_period * (self.requiredCPUs / self._client.availableCPUs)))

        module_logger.debug('cpu_quota = %d, cpu_period=%d'%(cpu_quota, cpu_period))

        kwargs = {'detach': True, 'mem_limit': str(self.requiredGBRAM) + 'g',
                  'cpu_period': cpu_period, 'cpu_quota': cpu_quota,
                  'name': 'dhpc_task_{}'.format(self.id)
                  }

        runtime = self._determine_runtime(self.requiredGPUs)
        if (runtime == 'nvidia'):
            kwargs['runtime'] = runtime

        volumes = self._create_path()
        if(volumes != {}):
            kwargs['volumes'] = volumes

        if(self.dockerImageType == 'WORKER'):
            port = self._extract_port()
            module_logger.debug('Using port config ' + str(port))
            kwargs['ports'] = port

        module_logger.debug('Container arguments are '+str(kwargs))
        if(runtime == 'oci' and self.requiredGPUs > 0):
            kwargs['device'] += "%s:'/dev/dri'" % self.accessibleGPUs['opencl'][0]
            module_logger.debug('Adding opencl device '+kwargs['device'])

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

    def remove_container(self):
        module_logger.debug('ENTER remove_container, removing container of task %s' % self.id)
        self._container.remove()

    def pause_container(self):
        module_logger.debug('ENTER pause_container, pausing container of task %s' % self.id)
        self._container.pause()

    def unpause_container(self):
        module_logger.debug('ENTER unpause_container, unpause container of task %s' % self.id)
        self._container.unpause()

    def stop_container(self):
        module_logger.debug('ENTER stop_container, stopping container of task %s' % self.id)
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
            "requiredOperatingSystem": self.requiredOperatingSystem
        }
