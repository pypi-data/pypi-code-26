from typing import Union

from sqlite_framework.sql.item.column import Column


class ColumnUtil:
    @staticmethod
    def name_if_column(value: Union[str, Column]):
        if isinstance(value, Column):
            return value.name
        return value
