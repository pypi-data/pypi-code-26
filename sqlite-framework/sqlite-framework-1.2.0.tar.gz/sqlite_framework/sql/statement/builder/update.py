from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.expression.parser import EXPRESSION_TYPE, ExpressionParser
from sqlite_framework.sql.statement.builder.base import StatementBuilder
from sqlite_framework.sql.statement.builder.clauses.table import TableClause
from sqlite_framework.sql.statement.builder.clauses.where import WhereClause


class Update(TableClause, WhereClause, StatementBuilder):
    def __init__(self):
        super().__init__()
        self._set = None
        self._update_all_rows = False

    def update_all_rows(self, update_all: bool = True):
        self._update_all_rows = update_all
        return self

    def set(self, column: Column, expr: EXPRESSION_TYPE):
        expr = ExpressionParser.parse(expr)
        self._set = "set {column_name} = {expr}".format(column_name=column.name, expr=expr.str())
        return self

    def build_sql(self):
        sql = "update {table} {set}".format(table=self._table, set=self._set)
        if self._not_none(self._where):
            sql += " {where}".format(where=self._where)
        elif not self._update_all_rows:
            raise Exception("Trying to build an UPDATE statement without a WHERE clause!\n"
                            "They are not allowed by default to avoid common mistakes, "
                            "as every table row would be updated.\n"
                            "If you know what you are doing and want to go along with it, "
                            "you can force it by calling update_all_rows().")
        return sql
