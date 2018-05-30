import contextlib
import logging
import psycopg2

from . import password_hasher

_logger = logging.getLogger(__name__)

_q_create_table = """
    CREATE TABLE IF NOT EXISTS users (
        email character varying(254) PRIMARY KEY,
        password character varying(128)
    );"""
_q_upd_password = "UPDATE users SET password=%s WHERE email=%s"
_q_ins_user = "INSERT INTO users (email, password) VALUES(%s, %s)"
_q_del_user = "DELETE FROM users WHERE email=%s"
_q_sel_password = "SELECT password FROM users WHERE email=%s"


class _DBConnection:
    """ Wraps a PostgreSQL database connection that reports crashes and tries
    its best to repair broken connections.

    NOTE: doesn't always work, but the failure scenario is very hard to
      reproduce. Also see https://github.com/psycopg/psycopg2/issues/263
    """

    def __init__(self, *args, **kwargs):
        self.conn_args = args
        self.conn_kwargs = kwargs
        self._conn = None
        self._connect()

    def _connect(self):
        if self._conn is None:
            self._conn = psycopg2.connect(*self.conn_args, **self.conn_kwargs)
            self._conn.autocommit = True

    def _is_usable(self):
        """ Checks whether the connection is usable.

        :returns boolean: True if we can query the database, False otherwise
        """
        try:
            self._conn.cursor().execute("SELECT 1")
        except psycopg2.Error:
            return False
        else:
            return True

    @contextlib.contextmanager
    def _connection(self):
        """ Contextmanager that catches tries to ensure we have a database
        connection. Yields a Connection object.

        If a :class:`psycopg2.DatabaseError` occurs then it will check whether
        the connection is still usable, and if it's not, close and remove it.
        """
        try:
            self._connect()
            yield self._conn
        except psycopg2.Error as e:
            _logger.critical('AUTHZ DatabaseError: {}'.format(e))
            if not self._is_usable():
                with contextlib.suppress(psycopg2.Error):
                    self._conn.close()
                self._conn = None
            raise e

    @contextlib.contextmanager
    def transaction_cursor(self):
        """ Yields a cursor with transaction.
        """
        with self._connection() as transaction:
            with transaction:
                with transaction.cursor() as cur:
                    yield cur

    @contextlib.contextmanager
    def cursor(self):
        """ Yields a cursor without transaction.
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                yield cur


class Users:
    """
    See :func:`psycopg2.connect` for constructor arguments.

    Usage:

    ::

        import dpuser

        users = dpuser.AuthzMap(**psycopgconf)

        users.add('myuser@example.com', 'secretpassword')
        users.set('myuser@example.com', 'newsecretpassword')
        users.verify_password('myuser@example.com', 'secretpassword')
        users.remove('myuser@example.com')

    """

    def __init__(self, *args, **kwargs):
        self._conn = _DBConnection(*args, **kwargs)

    def create(self):
        """ Create the tables for authz.
        """
        with self._conn.transaction_cursor() as cur:
            cur.execute(_q_create_table)
            if cur.rowcount > 0:
                _logger.info("User tables created")

    def add(self, email, password):
        """ Create a new user.

        :param username:
        :param password:
        :raise KeyError: If the user already exists
        """
        email = email.lower()
        if len(password) < 8:
            raise ValueError("Password too short")
        with self._conn.transaction_cursor() as cur:
            try:
                cur.execute(_q_ins_user, (email, password_hasher.encode(password)))
            except psycopg2.IntegrityError:
                raise KeyError("User already exists")

    def set(self, email, password):
        """ Set a new password for the given user.

        :param username:
        :param password:
        :raise KeyError: If the user doesn't exist
        """
        email = email.lower()
        if len(password) < 8:
            raise ValueError("Password too short")
        with self._conn.transaction_cursor() as cur:
            cur.execute(_q_upd_password, (password_hasher.encode(password), email))
            if cur.rowcount == 0:
                raise KeyError("User not found")

    def remove(self, email):
        """ Remove the given user.

        :param email:
        :raise KeyError: If the user doesn't exist.
        """
        email = str(email).lower()
        with self._conn.transaction_cursor() as cur:
            cur.execute(_q_del_user, (email,))
            if cur.rowcount == 0:
                raise KeyError("User not found")

    def verify_password(self, email, password):
        """Verifies a password."""
        email = str(email).lower()
        with self._conn.cursor() as cur:
            cur.execute(_q_sel_password, (email,))
            result = cur.fetchone()
        if result and result[0] is not None:
            return password_hasher.verify(password, result[0])
        return False
