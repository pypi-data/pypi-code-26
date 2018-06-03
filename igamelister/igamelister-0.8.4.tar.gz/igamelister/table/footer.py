from typing import Iterable

from igamelister.table.align import Align
from igamelister.table.sectionitem import SectionItem


class Footer(SectionItem):
    def __init__(self, content: Iterable, padding: int = None, align: Align = None):
        super().__init__(content, padding, align)
