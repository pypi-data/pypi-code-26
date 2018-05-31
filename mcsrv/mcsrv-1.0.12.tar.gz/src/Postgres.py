import asyncio
import aiopg
import logging
import os

logger = logging.getLogger(__name__)


class Postgres(object):
    """
    ENV requires:
    PG_HOST=127.0.0.1
    PG_PORT=5432
    PG_USER=guest
    PG_PASS=guest
    PG_DB=postgres
    """

    def __init__(self):
        logger.debug('Postgres init')
        self.loop = getattr(self, "loop", asyncio.get_event_loop())
        self.pool = self.loop.run_until_complete(self.__db_init())
        super(Postgres, self).__init__()

    def __del__(self):
        self.pool.close()
        deleter = getattr(super(Postgres, self), "__del__", None)
        if callable(deleter):
            deleter()

    async def __db_init(self):
        dsn = 'dbname={} user={} password={} host={} port={}'.format(
            os.getenv('PG_DB', 'postgres'),
            os.getenv('PG_USER', 'postgres'),
            os.getenv('PG_PASS', 'postgres'),
            os.getenv('PG_HOST', '127.0.0.1'),
            os.getenv('PG_PORT', 5432),
        )
        pool = await aiopg.create_pool(dsn, echo=os.getenv('LOG_LEVEL', None) == 'DEBUG')
        logger.info('Postgres connected')
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await self.create_tables(cursor)
        return pool

    async def create_tables(self, cursor):
        pass
