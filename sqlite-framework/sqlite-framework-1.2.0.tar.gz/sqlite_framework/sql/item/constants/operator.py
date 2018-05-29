from sqlite_framework.sql.item.base import NamedItem


class Operator(NamedItem):
    pass


# operators ordered by precedence (from highest to lowest)
# an empty line means a precedence jump

EQUAL = Operator("=")
IS = Operator("is")
IN = Operator("in")

AND = Operator("and")

OR = Operator("or")
