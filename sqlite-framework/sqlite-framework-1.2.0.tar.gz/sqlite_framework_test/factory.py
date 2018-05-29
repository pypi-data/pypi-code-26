from sqlite_framework.component.factory import SqliteStorageComponentFactory
from sqlite_framework_test.components.test import TestSqliteComponent


class TestSqliteStorageComponentFactory(SqliteStorageComponentFactory):
    def test(self) -> TestSqliteComponent:
        return self._initialized(TestSqliteComponent())
