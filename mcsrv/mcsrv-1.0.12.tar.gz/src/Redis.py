import asyncio
import aioredis
import logging
import os

logger = logging.getLogger(__name__)


class Redis(object):
    """
    ENV requires:
    REDIS_ADDRESS=redis://localhost
    REDIS_DB=
    REDIS_PASSWORD=
    """

    def __init__(self):
        logger.debug('Redis init')
        self.loop = getattr(self, "loop", asyncio.get_event_loop())
        self.redis = self.loop.run_until_complete(self.__redis_init())
        super(Redis, self).__init__()

    def __del__(self):
        self.redis.close()
        self.loop.run_until_complete(self.redis.wait_closed())
        deleter = getattr(super(Redis, self), "__del__", None)
        if callable(deleter):
            deleter()

    async def __redis_init(self):
        db = os.getenv('REDIS_DB', None)
        password = os.getenv('REDIS_PASSWORD', None)
        connect = {
            "address": os.getenv('REDIS_ADDRESS', 'redis://localhost'),
            "db": int(db) if db is not None else None,
            "password": password if password is not None and len(password) else None,
        }
        return await aioredis.create_redis_pool(**connect, loop=self.loop)

    async def lock(self, key, expire=30):
        if await self.redis.execute('SETNX', key, 1):
            await self.redis.execute('EXPIRE', key, int(expire))
            logger.info('Locked: `{}`'.format(key))
            return True
        else:
            logger.info('Already Locked: `{}`'.format(key))
            return False
