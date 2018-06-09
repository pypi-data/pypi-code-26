class Table:
    def __init__(self, name, header):
        self.name = name
        self.rows = []
        self.row_width = [len(el) for el in header]
        self.header = header

    def insert_row(self, elements):
        for i, elem in enumerate(elements):
            if len(str(elem)) > self.row_width[i]:
                self.row_width[i] = len(elem)
        diff = (len(self.header) - len(elements))
        if diff:
            elements += ['-'] * diff
        self.rows.append(elements)

    def sort(self, column=0, reverse=False):
        self.rows = sorted(self.rows, key=lambda elem: elem[column], reverse=reverse)

    def print_table(self, enum=False, sort_column=None, rev_sort=False, style='default'):
        styles = {'gothic': ['¤¤', '||', '='], 'default': ['+', '|', '-'], 'stars': ['/۩\\', '|||', '~']}
        plus = styles[style][0]
        vertical_border = styles[style][1]
        gorizontal_border = styles[style][2]

        if sort_column != None:
            self.sort(sort_column, rev_sort)
        row_width = self.row_width if not enum else [len(str(len(self.rows)))] + self.row_width
        border_line = ''
        header_line = vertical_border
        header = self.header if not enum else ['N'] + self.header
        for i, elem in enumerate(row_width):
            border_line += plus + gorizontal_border * (elem + 2)
            m = round(((elem - len(header[i]) + 2) / 2) - 0.1)
            n = round(((elem - len(header[i]) + 2) / 2) + 0.1)
            header_line += ' ' * m + header[i] + ' ' * n + vertical_border
        border_line += plus
        header = f'{border_line}\n{header_line}\n{border_line}'

        table = ''
        for k, line in enumerate(self.rows):
            table += vertical_border
            if enum:
                line = [k] + line
            for i, elem in enumerate(line):
                m = round(((row_width[i] - len(str(line[i])) + 2) / 2) - 0.1)
                n = round(((row_width[i] - len(str(line[i])) + 2) / 2) + 0.1)
                table += ' ' * m + str(line[i]) + ' ' * n + vertical_border
            table += f'\n'

        print(f'{self.name}\n{header}\n{table}{border_line}')
