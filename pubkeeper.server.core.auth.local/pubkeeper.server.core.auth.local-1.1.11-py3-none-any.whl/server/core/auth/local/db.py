from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command
from uuid import uuid4
from argparse import Namespace
from hashlib import sha256
import os

from .models import User, Token, Right


class Database(object):
    def __init__(self, database_uri, settings=None):
        self._settings = settings
        self._database_uri = database_uri

        try:
            self._engine = create_engine(self._database_uri)
            self._engine.connect()
            self._engine.dispose()
        except OperationalError:
            self._engine = create_engine(
                "{}/postgres".format(
                    self._database_uri[:self._database_uri.rfind('/')]),
                isolation_level="AUTOCOMMIT"
            )
            self._engine.execute('create database {}'.format(
                self._database_uri[self._database_uri.rfind('/') + 1:]))
            self._engine.dispose()
            self._engine = create_engine(self._database_uri)

        self._sessionmaker = sessionmaker(bind=self._engine)

        self.init_database()

        with self as session:
            has_root = \
                session.query(User).filter_by(username='root').first()

        if not has_root:
            self.seed_database()

    def __enter__(self):
        self._session = self._sessionmaker()
        return self._session

    def __exit__(self, exception_type, exception_value, traceback):
        self._session.close()
        self._engine.dispose()

    def init_database(self):
        file_directory = os.path.dirname(os.path.realpath(__file__))
        alembic_directory = os.path.join(file_directory, 'alembic')
        ini_path = os.path.join(file_directory, 'alembic.ini')

        # create Alembic config and feed it with paths
        config = Config(ini_path)
        config.set_main_option('script_location', alembic_directory)
        config.cmd_opts = Namespace()

        # If it is required to pass -x parameters to alembic
        x_arg = 'database_uri={}'.format(self._database_uri)
        if not hasattr(config.cmd_opts, 'x'):
            if x_arg is not None:
                setattr(config.cmd_opts, 'x', [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, 'x', None)

        revision = 'head'
        sql = False
        tag = None
        command.upgrade(config, revision, sql=sql, tag=tag)

    def seed_database(self):
        initial_password = self._settings.get(
            'initial_password', fallback='root')
        initial_token = self._settings.get(
            'initial_token', fallback=sha256(uuid4().bytes).hexdigest())

        user = User(username='root',
                    password=sha256(initial_password.encode()).hexdigest())

        token = Token(token=initial_token,
                      description='Default All Access Token')
        right = Right(token=initial_token, topic='**',
                      read=True, write=True)
        token.rights = [right]

        with self as session:
            session.add_all([user, token])
            session.commit()
