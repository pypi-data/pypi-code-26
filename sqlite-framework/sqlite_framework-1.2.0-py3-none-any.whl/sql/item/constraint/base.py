from sqlite_framework.sql.item.base import SqlItem


class BaseConstraint(SqlItem):
    def __init__(self, constraint: SqlItem, name: str = None):
        super().__init__()
        self.name = name
        self.constraint = constraint

    def str(self):
        return self._name() + self.constraint.str()

    def _name(self):
        if self.name is not None:
            return "constraint {name} ".format(name=self.name)
        return ""
