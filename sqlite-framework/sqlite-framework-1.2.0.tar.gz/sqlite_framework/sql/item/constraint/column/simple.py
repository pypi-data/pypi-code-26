from sqlite_framework.sql.item.base import StringItem
from sqlite_framework.sql.item.constraint.column.base import ColumnConstraint


class SimpleColumnConstraint(StringItem, ColumnConstraint):
    pass


PRIMARY_KEY = SimpleColumnConstraint("primary key")
NOT_NULL = SimpleColumnConstraint("not null")
UNIQUE = SimpleColumnConstraint("unique")
