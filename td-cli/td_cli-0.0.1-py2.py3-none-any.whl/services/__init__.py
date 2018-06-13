import configparser
import sqlite3
from abc import ABC, abstractmethod
from urllib.request import pathname2url


class Service(ABC):
    __slots__ = ('connection', 'cursor')

    def __init__(self):
        config = configparser.SafeConfigParser({'name': 'todo.db'})
        config.read('todo/todo.cfg')  # TODO: get full path and use .rc

        database_name = config.get('Database', 'name')
        db_uri = 'file:{}'.format(pathname2url(database_name))

        try:
            self.connection = sqlite3.connect('{}?mode=rw'.format(db_uri), uri=True)
            self.cursor = self.connection.cursor()
        except sqlite3.OperationalError:
            self._initialise_database(db_uri)

        self.cursor.execute("PRAGMA foreign_keys = ON")

    def _initialise_database(self, db_uri):
        self.connection = sqlite3.connect(db_uri, uri=True)
        self.cursor = self.connection.cursor()
        for cls in Service.__subclasses__():
            cls.initialise_table(self)
        self.connection.commit()

    @abstractmethod
    def initialise_table(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return False
        self.connection.close()


from .group import GroupService  # noqa: F401; isort: skip
from .todo import TodoService  # noqa: F401; isort: skip
