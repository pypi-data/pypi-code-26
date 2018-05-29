import sqlite3
from sqlite3 import Connection

from sqlite_framework.sql.result.row import ResultRow


class SqliteSession:
    def __init__(self, database_filename: str, debug: bool, enable_foreign_keys: bool = False):
        self.database_filename = database_filename
        self.debug = debug
        self.enable_foreign_keys = enable_foreign_keys
        self.inside_pending_context_manager = False
        # initialized in init to avoid creating sqlite objects outside the thread in which it will be operating
        self.connection = None  # type: Connection

    def init(self):
        self._init_connection()

    def _init_connection(self):
        if self.connection is not None:
            # already initialized, ignoring
            return
        self.connection = sqlite3.connect(self.database_filename)
        if self.debug:
            # print all sentences to stdout
            self.connection.set_trace_callback(lambda x: print(x))
        # disable implicit transactions as we are manually handling them
        self.connection.isolation_level = None
        # improved rows
        self.connection.row_factory = ResultRow
        # enable foreign keys before entering a transaction
        if self.enable_foreign_keys:
            self.connection.execute("PRAGMA foreign_keys = ON")
        if self.inside_pending_context_manager:
            self.__enter__()

    def context_manager(self):
        return self

    def __enter__(self):
        if self.connection is not None:
            self.connection.execute("begin")
        else:
            # the first init() operation may not yet have the connection created
            # so delay the begin until we create it
            self.inside_pending_context_manager = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.inside_pending_context_manager:
            self.inside_pending_context_manager = False
        if exc_type is None and exc_val is None and exc_tb is None:
            # no error
            self.connection.execute("commit")
        else:
            self.connection.execute("rollback")
