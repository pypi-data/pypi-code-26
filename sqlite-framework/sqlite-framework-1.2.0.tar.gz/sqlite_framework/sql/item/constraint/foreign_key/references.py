from sqlite_framework.sql.item.base import SqlItem
from sqlite_framework.sql.item.constraint.foreign_key.change import ReferenceChangeAction


class References(SqlItem):
    def __init__(self, table, on_delete: ReferenceChangeAction = None):
        # Specifying type of table param in docstring to avoid a cyclic dependency Table -> Column -/> Table
        """
        :type table: sqlite_framework.sql.item.table.Table
        """
        super().__init__()
        self.table = table
        self.on_delete = on_delete

    def str(self):
        reference = "references {table}".format(table=self.table.str())
        if self.on_delete:
            reference += " on delete {action}".format(action=self.on_delete.str())
        return reference
