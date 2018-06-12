from .widget import Widget

class Table(Widget):
    def __init__(self, element):
        super().__init__(element)

        self._xpath_prefix = "."
        if len(self._wrapper.xpath("./tbody[1]")) > 0:
            self._xpath_prefix = "./tbody[1]"

    def _xpath(self, pattern):
        return self._wrapper.xpath(self._xpath_prefix + pattern)

    @property
    def headers(self):
        header_prefix = "."
        if len(self._wrapper.xpath("./thead")) > 0:
            header_prefix = "./thead"

        return self._wrapper.xpath(header_prefix + "/tr[1]/th")

    @property
    def row_count(self):
        count = len(self._xpath("/tr"))
        if len(self._wrapper.xpath("./thead")) <= 0:
            if len(self.headers) > 0:
                count -= 1

        return count

    @property
    def col_count(self):
        elements = self._xpath("/tr[1]/td")
        if len(elements) <= 0:
            elements = self.headers

        return len(elements)

    def get_row(self, index):
        index += 1
        if len(self._wrapper.xpath("./thead")) <= 0:
            if len(self.headers) > 0:
                index += 1

        return self._xpath("/tr[%s]/td" % index)

    def get_col(self, index):
        index += 1
        start_pos = 0
        if len(self._wrapper.xpath("./thead")) <= 0:
            if len(self.headers) > 0:
                start_pos = 1

        return self._xpath("/tr/td[%s]" % index)[start_pos:]

    def get(self, row, col):
        return self.get_row(row)[col]
