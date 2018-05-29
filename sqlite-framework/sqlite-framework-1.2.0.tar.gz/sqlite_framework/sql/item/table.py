from collections import defaultdict

from sqlite_framework.sql.item.base import NamedItem
from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.constraint.table.table import TABLE_CONSTRAINT_TYPE


class Table(NamedItem):
    def __init__(self, name: str):
        super().__init__(name)
        self.columns = ColumnList()
        self.constraints = []
        self.column = self.columns.add

    def constraint(self, *constraints: TABLE_CONSTRAINT_TYPE):
        self.constraints.extend(constraints)


class ColumnList:
    def __init__(self):
        self._columns = []
        self._versions = defaultdict(list)

    def add(self, column: Column, version: int = 1):
        self._columns.append(column)
        self._versions[version].append(column)

    def get_all(self):
        return self._columns

    def get_with_version(self, version: int):
        return self._versions[version]
