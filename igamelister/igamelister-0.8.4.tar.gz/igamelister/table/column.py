from numbers import Number
from typing import Iterable

from igamelister.table.align import Align
from igamelister.table.sectionitem import SectionItem


class Column(SectionItem):
    def __init__(self, content: Iterable, padding: int = None, align: Align = None, width: Number = None,
                 label: str = None):
        super().__init__(content, padding, align, width)
        self.label = label
