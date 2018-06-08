from datetime import timedelta

from django.contrib.sessions.backends.base import SessionBase, CreateError
from cassandra import cluster
from django.conf import settings
from time import time
from django.utils import timezone

_SYCALLDB_CON = None


scylla_endpoint = getattr(settings, 'SCYLLA_HOST', '127.0.0.1')
scylla_port = getattr(settings, 'SCYLLA_PORT', '9042')
session_keyspace = getattr(settings, 'SESSION_KEYSPACE', 'sessions')
session_table = getattr(settings, 'SESSION_TABLE', 'sessions')
default_cluster_config = dict(
    contact_points=[scylla_endpoint, ],
    port=scylla_port,
    cql_version='3.3.1',
)
cluster_config = getattr(settings, 'SCYLLA_CLUSTER_CONFIG', default_cluster_config)


def get_connection(keyspace=None):
    global _SYCALLDB_CON

    if not _SYCALLDB_CON:
        _SYCALLDB_CON = cluster.Cluster(**cluster_config).\
            connect(keyspace)
    return _SYCALLDB_CON


_insert_statement = None
_select_statement = None
_delete_statement = None


def get_select_statement():
    global _select_statement

    if not _select_statement:
        query = 'SELECT * FROM {keyspace}.{table} WHERE session_id=?'.format(
            keyspace=session_keyspace, table=session_table)
        _select_statement = get_connection().prepare(query)
    return _select_statement


def get_insert_statement():
    global _insert_statement

    if not _insert_statement:

        query = 'UPDATE {keyspace}.{table} USING TTL ?' \
                'SET session_data=?, updated_at=? WHERE session_id=? ;'\
            .format(keyspace=session_keyspace, table=session_table)

        _insert_statement = get_connection().prepare(query)

    return _insert_statement


def get_delete_statement():
    global _delete_statement

    if not _delete_statement:
        query = 'DELETE FROM {keyspace}.{table} WHERE session_id=? ;'.\
            format(keyspace=session_keyspace, table=session_table)

        _delete_statement = get_connection().prepare(query)
    return _delete_statement


class SessionStore(SessionBase):

    @staticmethod
    def get_record(session_key):
        """
        Gets record from cassandra
        :return:
        """
        return get_connection().execute(get_select_statement(),
                                        [session_key])

    @staticmethod
    def insert_record(session_key, session_data, ttl):
        return get_connection().execute(get_insert_statement(),
                                        [ttl, session_data, int(time()), session_key])

    @staticmethod
    def delete_record(session_key):
        if session_key is not None:
            return get_connection().execute(get_delete_statement(), [session_key])

    def exists(self, session_key):
        if session_key is None:
            return False
        if len(list(self.get_record(session_key))) <= 0:
            return False
        return True

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if self.session_key is None:
            return self.create()
        session_data = self.encode(self._get_session(no_load=must_create))

        self.insert_record(self.session_key, session_data, self.get_expiry_age())

    def delete(self, session_key=None):
        if session_key is None and self.session_key is None:
                return
        self.delete_record(session_key or self.session_key)

    def load(self):
        if self.session_key is not None:
            response = list(self.get_record(self.session_key))

            if len(response) > 1:
                raise Exception("Multiple session_id")
            elif len(response) == 1:
                session_data = self.decode(response[0].session_data)
                time_now = timezone.now()
                time_one_minute_ahead = time_now + timedelta(seconds=60)
                if timezone.now() < session_data.get('_session_expiry',
                                                     time_one_minute_ahead):
                    return self.decode(response[0].session_data)

        self._session_key = None
        return {}

    @classmethod
    def clear_expired(cls):
        pass
