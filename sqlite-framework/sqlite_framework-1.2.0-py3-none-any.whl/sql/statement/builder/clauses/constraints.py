from sqlite_framework.sql.item.constraint.table.table import TABLE_CONSTRAINT_TYPE
from sqlite_framework.sql.statement.builder.clauses.base import BaseClause


class ConstraintsClause(BaseClause):
    def __init__(self):
        super().__init__()
        self._constraints = ()

    def constraints(self, *constraints: TABLE_CONSTRAINT_TYPE):
        self._constraints = (constraint.str() for constraint in constraints)
        return self
