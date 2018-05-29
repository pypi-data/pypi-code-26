from sqlite_framework.sql.item.table import Table
from sqlite_framework.sql.statement.builder.clauses.base import BaseClause


class TableClause(BaseClause):
    def __init__(self):
        super().__init__()
        self._table = None

    def table(self, table: Table):
        self._table = table.str()
        return self
