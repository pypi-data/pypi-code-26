import shutil
from itertools import zip_longest
from numbers import Number

from igamelister.table.align import Align
from igamelister.table.border import Border
from igamelister.table.column import Column
from igamelister.table.footer import Footer
from igamelister.table.header import Header
from igamelister.table.section import Section
from igamelister.text_helpers import repeat, pad, truncate


class Table:
    def __init__(self, margin: int = 0, padding: int = 1, align: Align = Align.Left, width: Number = 100.0):
        self._sections = []
        self._width = None

        if type(margin) is int:
            self.margin = margin
        else:
            raise TypeError(f"Expected type 'int', got '{type(margin).__name__}' instead.")

        if type(padding) is int:
            self.padding = padding
        else:
            raise TypeError(f"Expected type 'int', got '{type(padding).__name__}' instead.")

        if type(align) is Align:
            self.align = align
        else:
            raise TypeError(f"Expected type 'Align', got '{type(align).__name__}' instead.")

        if isinstance(width, Number):
            self.width = width
        else:
            raise TypeError(f"Expected type 'Number', got '{type(width).__name__}' instead.")

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        if type(value) is float:
            self.width_percent(value)
        elif type(value) is int:
            self.width_cols(value)
        else:
            raise TypeError(f"Expected type 'float' or 'int', got '{type(value).__name__}' instead.")

    @property
    def sections(self):
        return self._sections

    def width_percent(self, value: float):
        if type(value) is float:
            if value > 0.0:
                self._width = int((value / 100) * (shutil.get_terminal_size().columns - 1))
                self._set_section_widths()
            else:
                raise ValueError(f"Expected positive value, got {value} instead.")
        else:
            raise TypeError(f"Expected type 'float', got '{type(value).__name__}' instead.")

    def width_cols(self, value: int):
        if type(value) is int:
            if value > 0:
                self._width = value
                self._set_section_widths()
            else:
                raise ValueError(f"Expected positive value, got {value} instead.")
        else:
            raise TypeError(f"Expected type 'int', got '{type(value).__name__}' instead.")

    def add(self, section: Section):
        if isinstance(section, Section):
            section.width = self.width
            section.padding = self.padding if section.padding is None else section.padding
            for item in section.items:
                item.padding = section.padding if item.padding is None else item.padding
                item.align = section.align if item.align is None else item.align
            section.set_item_widths()
            self._sections.append(section)
        else:
            raise TypeError(f"Expected type 'Section', got '{type(section).__name__}' instead.")

    def draw(self):
        sec_count = len(self.sections)
        if sec_count == 0:
            return

        if self.sections[0].has_headers:
            self._draw_table_header_top()
        elif self.sections[0].has_columns:
            self._draw_section_columns_top(self.sections[0], is_top=True)

        for i in range(sec_count):
            section = self.sections[i]
            if section.has_headers:
                self._draw_section_headers(section)
                if section.has_columns:
                    self._draw_section_columns_top(section)

            if section.has_column_labels:
                self._draw_section_column_labels(section)

            if section.has_columns:
                self._draw_section_columns(section)

            if section.has_footers:
                if section.has_columns:
                    self._draw_section_columns_bottom(section)
                elif section.has_headers and not section.has_columns:
                    self._draw_section_sep(section)
                self._draw_section_footers(section)

            if i < sec_count - 1:
                self._draw_section_sep(section)

        if self.sections[-1].has_columns:
            self._draw_section_columns_bottom(self.sections[0], is_bottom=True)
        else:
            self._draw_table_bottom()

    def _draw_table_header_top(self):
        bdr = Border()
        line = repeat(bdr.t, self.width - (len(bdr.tl) + len(bdr.tr)))
        print(bdr.tl + line + bdr.tr)

    def _draw_table_bottom(self):
        bdr = Border()
        line = repeat(bdr.b, self.width - (len(bdr.bl) + len(bdr.br)))
        print(bdr.bl + line + bdr.br)

    def _draw_section(self, section):
        if section.has_headers:
            self._draw_section_headers(section)

        if section.has_columns:
            self._draw_section_columns(section)

    @staticmethod
    def _draw_section_sep(section):
        bdr = Border()
        if section.has_columns and not section.has_footers:
            col_lines = [repeat(bdr.mh, x.width + (x.padding * 2)) for x in section.items if type(x) is Column]
            print(bdr.ls + bdr.bs.join(col_lines) + bdr.rs)
        elif section.has_headers or section.has_footers:
            line = repeat(bdr.mh, section.width - (section.padding * 2))
            print(bdr.ls + line + bdr.rs)

    @staticmethod
    def _draw_section_headers(section):
        bdr = Border()
        headers = [x for x in section.items if type(x) is Header]
        count = 1
        for header in headers:
            padding = repeat(" ", header.padding)

            def header_gen():
                for content in header.content:
                    yield content.split("\n")

            for header_item in header_gen():
                for header_line in header_item:

                    header_text = pad(truncate(header_line, header.width), header.width, header.align.value)
                    header_row = bdr.l + padding + header_text + padding + bdr.r
                    print(header_row)

            if count < len(headers):
                line = repeat(bdr.mh, header.width + (header.padding * 2))
                print(bdr.ls + line + bdr.rs)
                count += 1

    @staticmethod
    def _draw_section_footers(section):
        bdr = Border()
        footers = [x for x in section.items if type(x) is Footer]
        count = 1
        for footer in footers:
            padding = repeat(" ", footer.padding)

            def footer_gen():
                for content in footer.content:
                    yield content.split("\n")

            for footer_item in footer_gen():
                for footer_line in footer_item:

                    footer_text = pad(truncate(footer_line, footer.width), footer.width, footer.align.value)
                    footer_row = bdr.l + padding + footer_text + padding + bdr.r
                    print(footer_row)

            if count < len(footers):
                line = repeat(bdr.mh, footer.width + (footer.padding * 2))
                print(bdr.ls + line + bdr.rs)
                count += 1

    @staticmethod
    def _draw_section_columns(section):
        bdr = Border()
        col_w = [x.width for x in section.items if type(x) is Column]
        col_p = [x.padding for x in section.items if type(x) is Column]
        col_a = [x.align for x in section.items if type(x) is Column]
        col_c = [x.content for x in section.items if type(x) is Column]
        col_rows = zip_longest(*col_c, fillvalue="")
        for row in col_rows:
            row_cols = []
            for i in range(len(row)):
                padding = repeat(" ", col_p[i])

                col_text = pad(truncate(row[i], col_w[i]), col_w[i], col_a[i].value)
                row_cols.append(padding + col_text + padding)
            print(bdr.l + bdr.mv.join(row_cols) + bdr.r)

    @staticmethod
    def _draw_section_column_labels(section):
        bdr = Border()
        lbl_w = [x.width for x in section.items if type(x) is Column]
        lbl_p = [x.padding for x in section.items if type(x) is Column]
        lbl_a = [x.align for x in section.items if type(x) is Column]
        lbl_c = [x.label for x in section.items if type(x) is Column]
        row_lbls = []
        for i in range(len(lbl_c)):
            padding = repeat(" ", lbl_p[i])
            col_text = pad(truncate(lbl_c[i], lbl_w[i]), lbl_w[i], lbl_a[i].value)
            row_lbls.append(padding + col_text + padding)
        print(bdr.l + bdr.mv.join(row_lbls) + bdr.r)

        col_lines = [repeat(bdr.mh, x.width + (x.padding * 2)) for x in section.items if type(x) is Column]
        print(bdr.ls + bdr.ms.join(col_lines) + bdr.rs)

    @staticmethod
    def _draw_section_columns_top(section: Section, is_top: bool = False):
        bdr = Border()
        if is_top:
            col_lines = [repeat(bdr.t, x.width + (x.padding * 2)) for x in section.items if type(x) is Column]
            print(bdr.tl + bdr.ts.join(col_lines) + bdr.tr)
        else:
            col_lines = [repeat(bdr.mh, x.width + (x.padding * 2)) for x in section.items if type(x) is Column]
            print(bdr.ls + bdr.ts.join(col_lines) + bdr.rs)

    @staticmethod
    def _draw_section_columns_bottom(section: Section, is_bottom: bool = False):
        bdr = Border()
        if is_bottom:
            col_lines = [repeat(bdr.b, x.width + (x.padding * 2)) for x in section.items if type(x) is Column]
            print(bdr.bl + bdr.bs.join(col_lines) + bdr.br)
        else:
            col_lines = [repeat(bdr.mh, x.width + (x.padding * 2)) for x in section.items if type(x) is Column]
            print(bdr.ls + bdr.bs.join(col_lines) + bdr.rs)

    def _set_section_widths(self):
        for section in self.sections:
            section._width = self.width
