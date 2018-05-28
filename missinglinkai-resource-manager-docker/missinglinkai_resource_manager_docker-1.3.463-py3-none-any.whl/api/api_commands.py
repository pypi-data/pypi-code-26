import json
import logging
from controllers import DockerWrapper

logger = logging.getLogger(__name__)


class CommandResponseError(Exception):
    def __init__(self, command, response):
        self.command = command
        self.response = response


async def send_command(send, command_name, command_version, **kwargs):
    await send(command=f"{command_name}:{command_version}", data=kwargs)


async def register_1(send, api_context, **kwargs):
    data = DockerWrapper.get().be_summary()
    response = await send(command="REGISTER:1", jwt=api_context.general.jwt, data=data, rpc=True)

    if response.get('ok', False):
        logger.info("Connected")
        return True
    raise CommandResponseError("register_1", response)


async def run_1(send, api_context, **kwargs):
    from .docker_execution import DockerExecution
    logger.info('RUN_1: %s', json.dumps(kwargs))
    kwargs['active_config'] = api_context
    await DockerExecution.create(send, **kwargs).run_manged()
    return True


async def on_connect(send, api_context, **kwargs):
    logger.debug('on_connect %s %s', api_context, kwargs)
    await send(jwt=api_context.general.jwt)


API_MAPPING = {
    'REGISTER:1': register_1,
    'RUN:1': run_1,
    '_on_connect': on_connect
}
