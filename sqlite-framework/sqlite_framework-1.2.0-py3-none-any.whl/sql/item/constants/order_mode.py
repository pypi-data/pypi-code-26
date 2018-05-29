from sqlite_framework.sql.item.base import NamedItem


class OrderMode(NamedItem):
    pass


ASC = OrderMode("asc")
DESC = OrderMode("desc")
