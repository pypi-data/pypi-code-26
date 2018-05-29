from sqlite_framework.sql.statement.builder.base import StatementBuilder
from sqlite_framework.sql.statement.builder.clauses.table import TableClause
from sqlite_framework.sql.statement.builder.clauses.where import WhereClause


class Delete(TableClause, WhereClause, StatementBuilder):
    def __init__(self):
        super().__init__()
        self._delete_all_rows = False

    def delete_all_rows(self, delete_all: bool = True):
        self._delete_all_rows = delete_all
        return self

    def build_sql(self):
        sql = "delete from {table}".format(table=self._table)
        if self._not_none(self._where):
            sql += " {where}".format(where=self._where)
        elif not self._delete_all_rows:
            raise Exception("Trying to build a DELETE statement without a WHERE clause!!\n"
                            "They are not allowed by default to avoid common mistakes, "
                            "as the entire table content would be deleted.\n"
                            "If you know what you are doing and want to go along with it, "
                            "you can force it by calling delete_all_rows().")
        return sql
