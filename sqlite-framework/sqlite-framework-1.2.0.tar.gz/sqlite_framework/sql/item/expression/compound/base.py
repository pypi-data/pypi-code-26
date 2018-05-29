from sqlite_framework.sql.item.expression.base import Expression
from sqlite_framework.sql.item.expression.parser import ExpressionParser


class CompoundExpression(Expression):
    def str(self):
        raise NotImplementedError()

    @staticmethod
    def parse(expr):
        return ExpressionParser.parse(expr)
