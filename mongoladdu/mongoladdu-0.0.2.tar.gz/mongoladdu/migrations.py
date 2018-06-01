import logging
import os
import re
from datetime import datetime
from importlib.machinery import SourceFileLoader

from pymongo import MongoClient
from yaml import load

logger = logging.getLogger(__name__)


class Paths:
    def __init__(self):
        self.migration = 'migrations'
        self.config = 'config.yml'
        self._validate()

    def config_path(self):
        return os.path.join(self.migration, self.config)

    def _validate(self):
        config_path = self.config_path()
        if not os.path.exists(config_path):
            logger.error('Unable to find config file %s for mongodb migrations!' % self.config_path())


class Config:
    def __init__(self, db_host, db_port, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name

    @classmethod
    def for_env(cls, paths: Paths, env: str) -> 'Config':
        config = load(open(paths.config_path(), 'r'))

        if env not in config:
            logger.error('Unable to find config for environment %s' % env)

        env_config = config[env]
        return Config(env_config['db_host'], env_config['db_port'], env_config['db_name'])

    @classmethod
    def for_values(cls, db_host, db_port, db_name):
        return cls(db_host, db_port, db_name)


class Db:
    @staticmethod
    def get(config: Config):
        return MongoClient(config.db_host, config.db_port)[config.db_name]


class Migration():
    def __init__(self, id, name, path):
        self.id = id
        self.name = name
        self.path = path

    def run(self, db):
        SourceFileLoader('migration', self.path).load_module().run(db)


class MongoRepo():
    def __init__(self, db):
        self.collection = db['db_migrations']

    def insert(self, migration):
        self.collection.insert({'id': migration.id, 'name': migration.name, 'execution_time': datetime.now()})

    def exists(self, id):
        return self.collection.find_one({'id': id})


class Migrations:
    PATTERN = '^(?P<id>[0-9]+)_(?P<name>[a-z0-9_]+)\.py$'

    def __init__(self, db, paths):
        self.db = db
        self.repo = MongoRepo(db)
        self.paths = paths

    def _all(self):
        migration_matchers = \
            [(re.match(Migrations.PATTERN, filename), filename) for filename in os.listdir(self.paths.migration)]

        migrations = [Migration(matcher.group('id'),
                                matcher.group('name'),
                                os.path.join(self.paths.migration, filename))
                      for matcher, filename in migration_matchers if matcher]

        return sorted(migrations, key=lambda migration: int(migration.id))

    def _yet_to_run(self):
        return [migration for migration in self._all() if not self.repo.exists(migration.id)]

    def run(self):
        yet_to_run = self._yet_to_run()
        logger.info('Found %i script(s) to run' % len(yet_to_run))
        for migration in yet_to_run:
            migration.run(self.db)
            self.repo.insert(migration)
            logger.info('Migrated %s' % migration.name)


class MongoLaddu:
    def __init__(self, env: str=None):
        self.env = env
        self.paths = Paths()

    def run(self):
        self._run(Config.for_env(self.paths, self.env))

    def run_for_config(self, db_host, db_port, db_name):
        self._run(Config.for_values(db_host, db_port, db_name))

    def _db(self, config):
        return Db.get(config)

    def _run(self, config):
        db = self._db(config)
        Migrations(db, self.paths).run()
