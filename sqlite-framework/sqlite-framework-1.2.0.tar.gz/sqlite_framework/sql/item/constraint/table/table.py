from typing import Union

from sqlite_framework.sql.item.constraint.base import BaseConstraint
from sqlite_framework.sql.item.constraint.table.base import TableConstraint


class Constraint(BaseConstraint):
    def __init__(self, constraint: TableConstraint):
        super().__init__(constraint)


TABLE_CONSTRAINT_TYPE = Union[TableConstraint, Constraint]
