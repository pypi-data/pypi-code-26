from sqlite_framework.sql.item.base import SqlItem


class Expression(SqlItem):
    def str(self):
        raise NotImplementedError()
