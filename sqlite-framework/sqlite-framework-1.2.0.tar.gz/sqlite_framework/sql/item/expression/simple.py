from sqlite_framework.sql.item.base import StringItem
from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.expression.base import Expression


class Literal(StringItem, Expression):
    def __init__(self, literal):
        super().__init__(str(literal))


class ColumnName(StringItem, Expression):
    def __init__(self, column: Column):
        super().__init__(column.name)
