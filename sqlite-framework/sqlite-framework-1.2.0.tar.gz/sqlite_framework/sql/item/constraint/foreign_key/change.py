from sqlite_framework.sql.item.base import NamedItem


class ReferenceChangeAction(NamedItem):
    pass


CASCADE = ReferenceChangeAction("cascade")
