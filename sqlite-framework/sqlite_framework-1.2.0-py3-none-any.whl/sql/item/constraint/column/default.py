from typing import Union

from sqlite_framework.sql.item.constraint.column.base import ColumnConstraint
from sqlite_framework.sql.item.expression.parser import EXPRESSION_TYPE, ExpressionParser


class Default(ColumnConstraint):
    def __init__(self, value: Union[EXPRESSION_TYPE, int, str], is_expr: bool = True):
        super().__init__()
        self.value = ExpressionParser.parse(value) if is_expr else value
        self.is_expr = is_expr

    def str(self):
        if self.is_expr:
            value = "({expr})".format(expr=self.value.str())
        else:
            value = str(self.value)
        return "default {value}".format(value=value)
