import mistune
import textwrap

from kooki.jars import search_file


def markdown_to_latex(content, document=None):
    renderer = LaTeXRenderer(document)
    markdown = mistune.Markdown(renderer=renderer)
    return markdown(content)


col_formatting = ''


class LaTeXRenderer(mistune.Renderer):

    def __init__(self, document, **kwargs):
        self.document = document
        super(LaTeXRenderer, self).__init__(**kwargs)

    def block_quote(self, text):
        return '{}'.format(text)

    def block_html(self, html):
        return ''

    def inline_html(self, text):
        return ''

    def header(self, text, level, raw):
        if level == 1:
            return '\n\\section{{{}}}\n\n'.format(text)
        if level == 2:
            return '\n\\subsection{{{}}}\n\n'.format(text)
        elif level == 3:
            return '\n\\subsubsection{{{}}}\n\n'.format(text)
        elif level == 4:
            return '\n\\paragraph{{{}}}\n\n'.format(text)
        elif level == 5:
            return '\n\\paragraph{{{}}}\n\n'.format(text)
        elif level == 6:
            return '\n\\subparagraph{{{}}}\n\n'.format(text)

    def hrule(self):
        return '\pagebreak'

    def list(self, body, ordered):
        if ordered:
            return '\\begin{{enumerate}}{}\\end{{enumerate}}\n\n'.format(body)
        else:
            return '\\begin{{itemize}}{}\\end{{itemize}}\n\n'.format(body)

    def list_item(self, text):
        return '\item {}\n'.format(text)

    def paragraph(self, text):
        text = text.replace('_', '\_')
        text = text.replace('&', '\&')
        return '{}\n\n'.format(text)

    def table(self, header, body):
        global col_formatting
        table_latex = textwrap.dedent('''\
            \\def\\arraystretch{1.5}
            \\begin{center}
            \\begin{tabular}{%s }
            \\hline
            %s\\hline
            %s\\hline
            \\end{tabular}
            \\end{center}
            ''')
        table_latex_filled = table_latex % (col_formatting, header, body)
        col_formatting = ''
        return table_latex_filled

    def table_row(self, content):
        content = content.split('&')[:-1]
        return '{}\\\\\n'.format('&'.join(content))

    def table_cell(self, content, **flags):
        global col_formatting
        if flags['header']:
            if flags['align'] == 'right':
                col_formatting += ' r'
            elif flags['align'] == 'center':
                col_formatting += ' c'
            elif flags['align'] == 'left':
                col_formatting += ' l'
            else:
                col_formatting += ' l'
            return '\\textbf{{{}}} & '.format(content)
        else:
            return '{} & '.format(content)

    def link(self, link, title, content):
        return '\\href{{{}}}{{{}}}'.format(link, content)

    def autolink(self, link, is_email=False):
        return '\\href{{{0}}}{{{0}}}'.format(link)

    def block_code(self, code, language):
        result = '\\begin{{verbatim}}\n{}\\end{{verbatim}}\n'.format(code)
        return result

    def codespan(self, text):
        return '\\texttt{{{}}}'.format(text)

    def double_emphasis(self, text):
        return '\\textbf{{{}}}'.format(text)

    def emphasis(self, text):
        return '\\emph{{{}}}'.format(text)

    def image(self, src, title, alt_text):
        if self.document:
            file_full_path = search_file(self.document.jars, self.document.recipe, src)
        else:
            file_full_path = src

        if alt_text == 'simple':

            return textwrap.dedent('''\
                \\includegraphics{{{}}}''').format(file_full_path)
        else:
            return textwrap.dedent('''\
                \\begin{{figure}}[!h]
                  \\includegraphics{{{}}}
                \\end{{figure}}''').format(file_full_path)

    def strikethrough(self, text):
        return '\sout{{{}}}'.format(text)

    def text(self, text):
        return text

    def linebreak(self):
        return '\\newline{}'

    def newline(self):
        return '\\par{}'

    def footnote_ref(self, key, index):
        return ''

    def footnote_item(self, key, text):
        return ''

    def footnotes(self, text):
        return ''
