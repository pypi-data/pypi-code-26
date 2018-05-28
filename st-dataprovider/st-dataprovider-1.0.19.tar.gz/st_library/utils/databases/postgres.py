import backoff
import psycopg2
from psycopg2.extras import DictCursor, NamedTupleCursor

from st_library.utils.generics.connectors import ConnectorContainer


_disconnect_errors = (psycopg2.InterfaceError, psycopg2.OperationalError,)
_backoff = backoff.on_exception(backoff.expo, _disconnect_errors, max_time=30, max_tries=30)


class Postgres(object):
    DictCursor = DictCursor
    NamedTupleCursor = NamedTupleCursor

    def __init__(self, name, host, port, username, password):
        self._name = name
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._conn = None
        self._cursor = None
        self._cursor_type = None

    def __repr__(self):
        return '<Postgres db "{}">'.format(self._name)

    def set_cursor_type(self, cursor_type):
        self._cursor_type = cursor_type

    @property
    def name(self):
        return self._name

    @_backoff
    def _get_connection(self):
        if self._conn and not self._conn.closed:
            return self._conn
        db_connection = self._do_get_connection()
        self._conn = db_connection
        return self._conn

    def _do_get_connection(self):
        return psycopg2.connect(database=self._name,
                                user=self._username,
                                password=self._password,
                                host=self._host, port=self._port)

    @_backoff
    def execute(self, *args, **kwargs):
        if self._cursor is None or self._cursor.closed:
            self._cursor = self._get_connection().cursor(cursor_factory=self._cursor_type)
        return self._cursor.execute(*args, **kwargs)

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, *args, **kwargs):
        return self._cursor.fetchmany(*args, **kwargs)

    def fetchone(self):
        return self._cursor.fetchone()

    @_backoff
    def commit(self):
        self._get_connection().commit()

    @_backoff
    def cancel(self):
        self._get_connection().cancel()

    @_backoff
    def close(self):
        self._get_connection().close()

    @_backoff
    def rollback(self):
        self._get_connection().rollback()


class PostgresContainer(ConnectorContainer):
    def _do_initialize_data(self):
        assert not len(self._list)

        params = self._fetch_param_dict([
            'psql_host', 'psql_name', 'psql_username', 'psql_password', 'psql_port'
        ])

        list_of_servers_params = [params]

        for server in list_of_servers_params:
            obj = Postgres(server['psql_name'], server['psql_host'],
                           int(server['psql_port']), server['psql_username'],
                           server['psql_password'])
            self._list.append(obj)
            self._dict[obj.name] = obj
