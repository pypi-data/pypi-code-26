from sqlite_framework.component.component import SqliteStorageComponent
from sqlite_framework.component.components.version_info import VersionInfoSqliteComponent
from sqlite_framework.component.migrate.migrator import SqliteComponentMigrator
from sqlite_framework.log.logger import SqliteLogger
from sqlite_framework.session.session import SqliteSession


class SqliteStorageComponentFactory:
    def __init__(self, session: SqliteSession, logger: SqliteLogger):
        self.connection = session.connection
        self.logger = logger
        self.version_info = self._version_info()  # type: VersionInfoSqliteComponent

    def _version_info(self):
        # set self.version_info now to not fail on _migrate
        self.version_info = VersionInfoSqliteComponent()
        return self._initialized(self.version_info)

    def _initialized(self, component: SqliteStorageComponent):
        component.set_connection(self.connection)
        self._migrate(component)
        return component

    def _migrate(self, component: SqliteStorageComponent):
        SqliteComponentMigrator(component, self.version_info, self.logger).migrate()
