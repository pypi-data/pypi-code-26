from typing import Union

from sqlite_framework.sql.item.constraint.base import BaseConstraint
from sqlite_framework.sql.item.constraint.column.base import COLUMN_CONSTRAINT_SUBTYPE


class Constraint(BaseConstraint):
    def __init__(self, constraint: COLUMN_CONSTRAINT_SUBTYPE):
        super().__init__(constraint)


COLUMN_CONSTRAINT_TYPE = Union[COLUMN_CONSTRAINT_SUBTYPE, Constraint]
