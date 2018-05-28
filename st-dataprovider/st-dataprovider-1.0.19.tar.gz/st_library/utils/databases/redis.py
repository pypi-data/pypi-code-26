import redis

from st_library.utils.generics.connectors import ConnectorContainer


class Redis(object):
    def __init__(self, db, host, port, password):
        self._db = db
        self._host = host
        self._port = port
        self._password = password
        self._redis = redis.StrictRedis(host=host, port=port, db=db, password=password)

    def __repr__(self):
        return '<Postgres db "{}">'.format(self._db)

    @property
    def db(self):
        return self.db

    @property
    def redis(self):
        return self._redis


class RedisContainer(ConnectorContainer):
    def _do_initialize_data(self):
        assert not len(self._list)

        params = self._fetch_param_dict([
            'redis_db', 'redis_host', 'redis_password', 'redis_port'
        ])

        list_of_servers_params = [params]

        for server in list_of_servers_params:
            obj = Redis(server['redis_db'], server['redis_host'],
                        int(server['redis_port']),
                        server['psql_password'])
            self._list.append(obj)
