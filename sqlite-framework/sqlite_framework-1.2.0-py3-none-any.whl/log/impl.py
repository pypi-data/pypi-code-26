from sqlite_framework.log.logger import SqliteLogger


class NoSqliteLogger(SqliteLogger):
    def migration(self, component: str, migration_type: str, old_version: int, new_version: int,
                  about_to_migrate_to_version: int):
        pass


class BasicSqliteLogger(SqliteLogger):
    def __init__(self, send_func: callable = print):
        self.send_func = send_func

    def migration(self, component: str, migration_type: str, old_version: int, new_version: int,
                  about_to_migrate_to_version: int):
        text = \
            "---\n" \
            "About to migrate to version {about_to_migrate_to_version}\n" \
            "Component: {component}\n" \
            "Type: {type}\n" \
            "Old version: {old_version}\n" \
            "New version: {new_version}\n" \
            "---" \
            .format(
                about_to_migrate_to_version=about_to_migrate_to_version,
                component=component,
                type=migration_type,
                old_version=old_version,
                new_version=new_version
            )
        self.send_func(text)
