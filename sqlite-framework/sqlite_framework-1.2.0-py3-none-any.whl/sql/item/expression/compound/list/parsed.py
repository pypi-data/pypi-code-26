from sqlite_framework.sql.item.expression.base import Expression


DEFAULT_SEPARATOR = ", "
DEFAULT_BEFORE = ""
DEFAULT_AFTER = ""


class ParsedExpressionList(Expression):
    def __init__(self, *expressions: Expression, separator: str = DEFAULT_SEPARATOR,
                 before: str = DEFAULT_BEFORE, after: str = DEFAULT_AFTER):
        super().__init__()
        self.expressions = expressions
        self.separator = separator
        self.before = before
        self.after = after

    def str(self):
        expressions = (
            "{expr}".format(expr=expr.str())
            for expr in self.expressions
        )
        expressions = self.separator.join(expressions)
        return "{before}{expressions}{after}"\
            .format(before=self.before, expressions=expressions, after=self.after)
