from sqlite_framework.sql.item.expression.base import Expression
from sqlite_framework.sql.statement.builder.select import Select


class SelectExpression(Expression):
    def __init__(self, select: Select):
        super().__init__()
        self.select = select

    def str(self):
        return "({select})".format(select=self.select.build_sql())
