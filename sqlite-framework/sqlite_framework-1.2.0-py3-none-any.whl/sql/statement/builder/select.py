from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.expression.parser import EXPRESSION_TYPE, ExpressionParser
from sqlite_framework.sql.item.table import Table
from sqlite_framework.sql.statement.builder.base import StatementBuilder
from sqlite_framework.sql.statement.builder.clauses.order_by import OrderByClause
from sqlite_framework.sql.statement.builder.clauses.where import WhereClause


class Select(WhereClause, OrderByClause, StatementBuilder):
    """
    IMPORTANT:
    All arguments are added to the sql statement in an unsafe way!
    So, untrusted input MUST NOT be passed to them.
    Their values should ideally be static string literals.
    If computed at runtime, they MUST come from a TOTALLY trusted source (like another module string constant
    or an admin-controlled configuration value).
    """

    def __init__(self):
        super().__init__()
        self._fields = "*"
        self._from = None
        self._join = None
        self._group_by = None
        self._limit = None
        self._other = None

    def fields(self, *fields: EXPRESSION_TYPE):
        self._fields = ExpressionParser.parse(fields).str()
        return self

    def table(self, table: Table):
        self._from = "from {table}".format(table=table.str())  # unsafe formatting
        return self

    def join(self, table: Table, on: EXPRESSION_TYPE = None, using: Column = None, full_cartesian: bool = False):
        join = "join {table}".format(table=table.str())  # unsafe formatting
        assert on is None or using is None, "both 'on' and 'using' cannot be specified at the same time"
        if on is not None:
            join += " on {on}".format(on=ExpressionParser.parse(on).str())
        elif using is not None:
            join += " using ({using})".format(using=using.name)
        elif not full_cartesian:
            raise Exception(
                "Trying to create a join without adding 'on' nor 'using' clauses. "
                "This results in a full cartesian product of both tables, "
                "and that is probably not what you want to achieve. "
                "To avoid it, set either an 'on' condition or a 'using' column. "
                "If you really want to perform the full cartesian product, "
                "set the 'full_cartesian' parameter to true."
            )
        if self._not_none(self._join):
            self._join += " " + join
        else:
            self._join = join
        return self

    def group_by(self, *expr: EXPRESSION_TYPE):
        expr = ExpressionParser.parse(expr)
        self._group_by = "group by {expr}".format(expr=expr.str())  # unsafe formatting
        return self

    def limit(self, expr: EXPRESSION_TYPE):
        expr = ExpressionParser.parse(expr)
        self._limit = "limit {expr}".format(expr=expr.str())  # unsafe formatting
        return self

    def other(self, clauses: str):
        self._other = clauses  # unsafe formatting
        return self

    def build_sql(self):
        select = "select {fields}".format(fields=self._fields)  # unsafe formatting
        clauses = [
            select,
            self._from,
            self._join,
            self._where,
            self._group_by,
            self._order_by,
            self._limit,
            self._other
        ]
        clauses = filter(self._not_none, clauses)
        return " ".join(clauses)
