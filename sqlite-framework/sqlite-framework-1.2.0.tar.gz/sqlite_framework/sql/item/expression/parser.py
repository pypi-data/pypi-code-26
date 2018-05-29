from typing import Union, Iterable

from sqlite_framework.sql.item.column import Column
from sqlite_framework.sql.item.expression.base import Expression
from sqlite_framework.sql.item.expression.compound.list.parsed import ParsedExpressionList
from sqlite_framework.sql.item.expression.simple import ColumnName, Literal


EXPRESSION_TYPE_SIMPLE = Union[Expression, Column, str, int]
EXPRESSION_TYPE_LIST = Iterable[EXPRESSION_TYPE_SIMPLE]
EXPRESSION_TYPE = Union[EXPRESSION_TYPE_SIMPLE, EXPRESSION_TYPE_LIST]


class ExpressionParser:
    @classmethod
    def parse(cls, expr: EXPRESSION_TYPE):
        # importing Select here to avoid cyclic dependency Select -> ExpressionParser -/> Select
        from sqlite_framework.sql.statement.builder.select import Select
        from sqlite_framework.sql.item.expression.select import SelectExpression
        if isinstance(expr, Expression):
            return expr
        elif isinstance(expr, Select):
            return SelectExpression(expr)
        elif isinstance(expr, Column):
            return ColumnName(expr)
        elif isinstance(expr, (str, int)):
            return Literal(expr)
        elif isinstance(expr, Iterable):
            return cls.parse_list(expr)
        raise Exception("could not parse the expression")

    @classmethod
    def parse_list(cls, expr_list: EXPRESSION_TYPE_LIST):
        parsed_expressions = (cls.parse(expr) for expr in expr_list)
        return ParsedExpressionList(*parsed_expressions)
