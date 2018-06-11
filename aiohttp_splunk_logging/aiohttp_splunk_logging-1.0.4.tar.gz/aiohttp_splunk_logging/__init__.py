from .client import *
from .handler import *
from .middleware import *
from .setup import *

async def create_event(*args, **kwargs):
    from logging import getLogger
    logger = getLogger()
    for handler in reverse(logger.handlers):
        if type(handler) == SplunkHandler:
            await handler.splunk_interface.create_event(*args, **kwargs)