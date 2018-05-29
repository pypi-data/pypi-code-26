from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.constraint.table.base import ColumnListTableConstraint


class Unique(ColumnListTableConstraint):
    def __init__(self, *columns: Column):
        super().__init__("unique", *columns)
