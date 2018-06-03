from igamelister.table.align import Align
from igamelister.table.border import Border
from igamelister.table.column import Column
from igamelister.table.footer import Footer
from igamelister.table.header import Header
from igamelister.table.sectionitem import SectionItem


class Section:
    def __init__(self, padding: int = None, align: Align = Align.Left):
        self._items = []

        self.width = None

        if padding is not None:
            if type(padding) is int:
                self.padding = padding
            else:
                raise TypeError(f"Expected type 'int', got '{type(padding).__name__}' instead.")
        else:
            self.padding = None

        if type(align) is Align:
            self.align = align
        else:
            raise TypeError(f"Expected type 'Align', got '{type(align).__name__}' instead.")

    @property
    def items(self):
        return self._items

    @property
    def has_headers(self):
        return bool(len([x for x in self.items if type(x) is Header]))

    @property
    def has_columns(self):
        return bool(len([x for x in self.items if type(x) is Column]))

    @property
    def has_column_labels(self):
        for x in self.items:
            if type(x) is Column:
                if x.label is not None:
                    return True
        return False

    @property
    def has_footers(self):
        return bool(len([x for x in self.items if type(x) is Footer]))

    def add(self, item: SectionItem):
        if isinstance(item, SectionItem):
            self._items.append(item)
        else:
            raise TypeError(f"Expected type 'SectionItem', got '{type(item).__name__}' instead.")

    def set_item_widths(self):
        bdr = Border()
        outer_border_width = len(bdr.l) + len(bdr.r)
        inner_border_width = len(bdr.mv)
        padding_width = self.padding * 2
        inner_section_width = self.width - outer_border_width
        header_width = inner_section_width - padding_width
        footer_width = header_width

        if self.has_headers:
            # set all Header instances to the full table width
            for item in self.items:
                if type(item) is Header:
                    item.width = header_width

        if self.has_columns:
            # set all Column instances with percentage (float) widths based on
            # left over available space after Column instances with
            # fixed width (int) widths.
            columns = [x for x in self.items if type(x) is Column]
            columns_border_width = inner_border_width * (len(columns)) - 1
            columns_padding = padding_width * len(columns)
            total_columns_width = inner_section_width - (columns_border_width + columns_padding)

            available_width = total_columns_width - sum([x.width for x in columns if type(x.width) is int])
            for column in columns:
                if type(column.width) is float:
                    float_width = column.width
                    column.width = int((column.width / 100) * available_width)
                    if column.width == 0:
                        raise ValueError(f"Not enough available space ({available_width}) "
                                         f"for percentage based column width ({float_width}%).")

            # set all other Column instances with no widths set (auto) based on
            # left over available space after all other Column instance widths
            # have been set.
            available_width = total_columns_width - sum([x.width for x in columns if x.width is not None])
            auto_width_column_count = len([x for x in columns if x.width is None])
            available_remainder = available_width % auto_width_column_count
            if available_width < auto_width_column_count:
                raise ValueError(f"Not enough available space ({available_width}) "
                                 f"for auto generated width columns ({auto_width_column_count}).")
            for column in columns:
                if column.width is None:
                    column.width = int(available_width / auto_width_column_count)
                    if available_remainder > 0:
                        column.width += 1
                        available_remainder -= 1

        if self.has_footers:
            # set all Footer instances to the full table width
            for item in self.items:
                if type(item) is Footer:
                    item.width = footer_width
