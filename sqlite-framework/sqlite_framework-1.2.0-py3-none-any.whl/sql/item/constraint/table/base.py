from sqlite_framework.sql.item.base import SqlItem
from sqlite_framework.sql.item.column import Column


class TableConstraint(SqlItem):
    def str(self):
        raise NotImplementedError()


class ColumnListTableConstraint(TableConstraint):
    def __init__(self, constraint_type: str, *columns: Column):
        super().__init__()
        self.type = constraint_type
        self.columns = columns

    def str(self):
        columns = ", ".join(column.name for column in self.columns)
        return "{type} ({columns})".format(type=self.type, columns=columns)
