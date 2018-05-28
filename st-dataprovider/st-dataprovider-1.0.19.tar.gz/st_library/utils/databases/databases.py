from st_library.utils.databases.postgres import PostgresContainer
from st_library.utils.databases.redis import RedisContainer


class Databases(object):
    def __init__(self):
        self.psql_dbs = PostgresContainer()
        self.redis_dbs = RedisContainer()
