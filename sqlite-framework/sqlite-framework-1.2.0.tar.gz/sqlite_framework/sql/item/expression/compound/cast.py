from sqlite_framework.sql.item.constants.type import Type
from sqlite_framework.sql.item.expression.compound.base import CompoundExpression
from sqlite_framework.sql.item.expression.parser import EXPRESSION_TYPE


class Cast(CompoundExpression):
    def __init__(self, expr: EXPRESSION_TYPE, type: Type):
        super().__init__()
        self.expr = self.parse(expr)
        self.type = type

    def str(self):
        return "cast({expr} as {type})".format(expr=self.expr.str(), type=self.type.str())
