from .RMQ import RMQ
import time
import logging

import os

logger = logging.getLogger(__name__)


class Logger(RMQ):
    """
    ENV requires:
    RMQ_HOST=127.0.0.1
    RMQ_PORT=5672
    RMQ_USER=guest
    RMQ_PASS=guest
    RMQ_EXCHANGE=
    RMQ_EXCHANGE_TYPE=direct
    RMQ_LOGGER=
    """

    def __init__(self):
        logger.debug('Logger init')
        self.logger_queue = os.getenv('RMQ_LOGGER', '')
        super(Logger, self).__init__()
        if self.logger_queue:
            self.loop.run_until_complete(self.queue_declare([self.logger_queue]))

    async def log(self, uid, message, level=None):
        if self.logger_queue:
            data = {
                "id": uid,
                "time": int(time.time()),
                "level": str(level),
                "message": message
            }
            await self.publish(data, self.logger_queue)
