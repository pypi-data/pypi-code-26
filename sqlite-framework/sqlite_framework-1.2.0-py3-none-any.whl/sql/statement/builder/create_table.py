import itertools

from sqlite_framework.sql.item.table import Table
from sqlite_framework.sql.statement.builder.base import StatementBuilder
from sqlite_framework.sql.statement.builder.clauses.columns import ColumnsClause
from sqlite_framework.sql.statement.builder.clauses.constraints import ConstraintsClause
from sqlite_framework.sql.statement.builder.clauses.table import TableClause


class CreateTable(TableClause, ColumnsClause, ConstraintsClause, StatementBuilder):
    """
    IMPORTANT:
    Table name and column definitions are added to the sql statement in an unsafe way!
    So, untrusted input MUST NOT be passed to them.
    Their values should ideally be static string literals.
    If computed at runtime, they MUST come from a TOTALLY trusted source (like another module string constant
    or an admin-controlled configuration value).
    """

    def from_definition(self, table: Table):
        self.table(table)
        self.columns(*table.columns.get_all())
        self.constraints(*table.constraints)
        return self

    def build_sql(self):
        columns_and_constraints = itertools.chain(self._columns_definitions, self._constraints)
        columns_and_constraints = ", ".join(columns_and_constraints)
        return "create table {name} ({columns_and_constraints})"\
            .format(name=self._table, columns_and_constraints=columns_and_constraints)
