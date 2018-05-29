from typing import Union

from sqlite_framework.sql.item.base import SqlItem
from sqlite_framework.sql.item.constants.type import Type, INTEGER
from sqlite_framework.sql.item.constraint.column.column import COLUMN_CONSTRAINT_TYPE
from sqlite_framework.sql.item.constraint.column.simple import PRIMARY_KEY, NOT_NULL, SimpleColumnConstraint


class Column(SqlItem):
    def __init__(self, name: str, type: Type, *constraints: Union[COLUMN_CONSTRAINT_TYPE, str]):
        super().__init__()
        self.name = name
        self.type = type
        self.constraints = tuple(map(self._convert_legacy_constraints, constraints)) if constraints else ()

    @staticmethod
    def _convert_legacy_constraints(constraint: Union[COLUMN_CONSTRAINT_TYPE, str]):
        if isinstance(constraint, str):
            return SimpleColumnConstraint(constraint)
        return constraint

    def str(self):
        column = "{name} {type}".format(name=self.name, type=self.type.str())
        if self.constraints:
            constraints = " ".join(constraint.str() for constraint in self.constraints)
            column += " {constraints}".format(constraints=constraints)
        return column


ROWID = Column("rowid", INTEGER, PRIMARY_KEY, NOT_NULL)
