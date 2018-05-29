from sqlite_framework.sql.item.base import NamedItem


class ConflictResolution(NamedItem):
    pass


REPLACE = ConflictResolution("replace")
IGNORE = ConflictResolution("ignore")
