from sqlite_framework.sql.item.base import NamedItem


class Type(NamedItem):
    pass


INTEGER = Type("integer")
TEXT = Type("text")
REAL = Type("real")
