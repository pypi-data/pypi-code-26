from typing import Union

from sqlite_framework.sql.item.base import SqlItem
from sqlite_framework.sql.item.constraint.foreign_key.references import References


class ColumnConstraint(SqlItem):
    def str(self):
        raise NotImplementedError()


COLUMN_CONSTRAINT_SUBTYPE = Union[ColumnConstraint, References]
