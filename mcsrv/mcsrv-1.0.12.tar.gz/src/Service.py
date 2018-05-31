import asyncio
import logging
import os

logger = logging.getLogger(__name__)


class Service(object):

    def __init__(self, worker, loop=None):
        logging.basicConfig(
            level=logging.getLevelName(os.getenv('LOG_LEVEL', 'INFO')),
            format="%(asctime)-15s [{}] %(levelname)8s %(name)20s %(message)s".format(worker)
        )
        logger.debug('Service init')

        if loop is None:
            self.loop = getattr(self, "loop", asyncio.get_event_loop())
        else:
            self.loop = loop
        super(Service, self).__init__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
