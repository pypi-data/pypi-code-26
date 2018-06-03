from numbers import Number
from typing import Iterable

from igamelister.table.align import Align


class SectionItem:
    def __init__(self, content: Iterable, padding: int = None, align: Align = None, width: Number = None):
        if isinstance(content, Iterable):
            if type(content) is str:
                self.content = [content]
            else:
                self.content = content
        else:
            raise TypeError(f"Expected type 'Iterable', got '{type(content).__name__}' instead.")

        self.padding = padding
        self.align = align
        self.width = width
