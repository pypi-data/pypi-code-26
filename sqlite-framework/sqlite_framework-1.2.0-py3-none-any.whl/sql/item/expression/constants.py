from sqlite_framework.sql.item.expression.simple import Literal


NULL = Literal("null")

CURRENT_UNIX_TIMESTAMP = Literal("strftime('%s', 'now')")
