from sqlite_framework.component.migrate.strategy import SqliteMigrationStrategy


class SqliteNoMigration(SqliteMigrationStrategy):
    def migrate(self):
        # nothing to do
        pass
