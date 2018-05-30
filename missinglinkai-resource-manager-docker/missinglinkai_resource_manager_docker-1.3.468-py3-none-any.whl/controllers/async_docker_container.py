import asyncio

from .docker_controller import logger
from .docker_wrapper import DockerWrapper
from .log_generator import LogGenerator
from .stat_generator import StatGenerator


class AsyncDockerContainer(object):
    @classmethod
    def get_container_env(cls, active_config):
        return {
            'ML': 'True',
            'ML_CLUSTER_ID': active_config.general.cluster_id,
            'ML_CLUSTER_MANAGER': active_config.general.ws_server}

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    @classmethod
    async def create_and_run(cls, **kwargs):
        run_prefix = kwargs.pop('prefix', kwargs['image'])
        return await cls.create(**kwargs).run_with_callbacks(run_prefix)

    def __init__(self, **kwargs):
        self.active_config = kwargs.pop('active_config')
        internal_env = self.get_container_env(self.active_config)
        env = kwargs.pop('env', {})
        env.update(internal_env)
        labels = kwargs.pop('labels', {})
        labels.update(internal_env)
        self.image = kwargs.pop('image')
        self.command = kwargs.pop('command', None)
        self.env = env
        self.volumes = kwargs.pop('volumes', None)
        self.labels = labels
        self.container = None
        self.exit = None
        self.container_id = None
        self.logs = None
        self.kill_on_exit = kwargs.pop('kill_on_exit', False)
        self.work_dir = kwargs.pop('workdir', None)
        self.runtime = None
        self.docker = kwargs.pop('docker_client', DockerWrapper.get())
        if kwargs.pop('gpu', False):
            self.runtime = 'nvidia'
        self.log_cb = self.safe_get_callback(kwargs.pop('log_callback', None))
        self.stats_cb = self.safe_get_callback(kwargs.pop('stats_call_back', None), 5)

    def __aiter__(self):
        return self

    @classmethod
    def safe_get_callback(cls, cb, empty_sleep=0):
        async def empty_func():
            await asyncio.sleep(empty_sleep)

        return cb or empty_func

    async def __aenter__(self):
        service_data = self.docker.be_summary()
        max_memory = int(service_data['cpu']['memory'] * 0.9)
        logger.info('Max memort for container: %s', max_memory)
        self.container = self.docker.create_container(
            image=self.image,
            command=self.command,
            stdin_open=False,
            detach=True,
            environment=self.env,
            labels=self.labels,
            volumes=self.volumes,
            working_dir=self.work_dir,
            mem_limit=max_memory,
            runtime=self.runtime
        )
        self.container_id = self.container.name
        self.container.start()
        self.logs = LogGenerator(self.container)
        self.stats_generator = StatGenerator(self.container)
        return self

    def remove_and_cleanup_container(self):
        container_volumes = self.container.attrs.get('Mounts', [])
        self.container.remove()
        for cont_volume in container_volumes:
            if 'Name' not in cont_volume:
                logger.info('remove_and_cleanup_container: Skipping %s ', cont_volume)
                continue

            name = cont_volume['Name']
            if name not in self.volumes:
                volume_obj = self.docker.volume(name)
                if volume_obj is not None:
                    volume_obj.remove()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.container is None:
            logger.error(f'Failed to obtain container status for {self.container_id}, container not found')
            return

        logger.debug(f"{self.container_id}:  __aexit__ state {self.container_id}: {self.container.status}")
        if self.container.status != 'exited':
            if self.kill_on_exit:
                self.container.kill()
                self.exit = (self.container.status, self.container.wait())
            else:
                logger.error(f'Leaving container id {cont_done.name} Running')
        else:
            self.exit = (self.container.status, self.container.wait())
        if self.exit is not None:
            self.remove_and_cleanup_container()
        await asyncio.sleep(0)

    async def run_with_callbacks(self, prefix):

        async with self as context:
            logger.debug('%s: DOCKER: run %s', self.container.name, prefix)

            async def _do_logs():
                async for line in context.logs:
                    await  asyncio.sleep(0)
                    await  context.log_cb(line)

            async def _do_stats():
                async for x in context.stats_generator:
                    await  asyncio.sleep(0)
                    await context.stats_cb(x)

            await  asyncio.wait([_do_logs(), _do_stats()])
            self.container.reload()
            logger.debug('%s: DOCKER: DONE %s', self.container.name, self.container.status)

        return self
