import asyncio
import aioamqp
import logging
try:
    import ujson as json
except ImportError:
    import json

import os

logger = logging.getLogger(__name__)


class RMQ(object):
    """
    ENV requires:
    RMQ_HOST=127.0.0.1
    RMQ_PORT=5672
    RMQ_USER=guest
    RMQ_PASS=guest
    or
    RMQ_ADDRESS=amqp://localhost

    RMQ_EXCHANGE=
    RMQ_EXCHANGE_TYPE=direct
    """

    def __init__(self):
        logger.debug('RMQ init')
        self.loop = getattr(self, "loop", asyncio.get_event_loop())
        self.exchange = os.getenv('RMQ_EXCHANGE', '')
        self.transport, self.protocol, self.channel = self.loop.run_until_complete(self.__rmq_init())
        super(RMQ, self).__init__()

    def __del__(self):
        self.loop.run_until_complete(self.__rmq_close())
        deleter = getattr(super(RMQ, self), "__del__", None)
        if callable(deleter):
            deleter()

    async def __rmq_close(self):
        await self.channel.close()
        await self.protocol.close()
        self.transport.close()

    async def __rmq_init(self):
        if os.getenv('RMQ_ADDRESS'):
            transport, protocol = await aioamqp.from_url(os.getenv('RMQ_ADDRESS'))
        else:
            rmq = {
                "host": os.getenv('RMQ_HOST', '127.0.0.1'),
                "port": os.getenv('RMQ_PORT', 5672),
                "login": os.getenv('RMQ_USER', 'guest'),
                "password": os.getenv('RMQ_PASS', 'guest'),
            }
            transport, protocol = await aioamqp.connect(**rmq)
        logger.info('RMQ connected')
        channel = await protocol.channel()

        if self.exchange != '':
            type_name = os.getenv('RMQ_EXCHANGE_TYPE', 'direct')
            await channel.exchange_declare(exchange_name=self.exchange, type_name=type_name)

        return transport, protocol, channel

    async def queue_declare(self, queues):
        for queue_name in queues:
            await self.channel.queue_declare(queue_name=queue_name)
            if self.exchange != '':
                await self.channel.queue_bind(queue_name, self.exchange, queue_name)

    async def publish(self, data, queue, headers=None):
        await self.channel.basic_publish(
            payload=json.dumps(data),
            exchange_name=str(self.exchange),
            routing_key=queue,
            properties={
                'headers': headers if headers else {}
            }
        )
        logger.debug("Published `{}`".format(data))