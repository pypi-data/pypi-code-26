#!/usr/bin/env python3


"""
Pandoc filter for converting spaces to non-breakable spaces in LaTeX
for french ponctuation
"""

from panflute import Space, Str, RawInline, run_filter


def spaces(elem, doc):
    # Is it in the right format and is it a Space?
    if doc.format in ['latex', 'beamer'] and isinstance(elem, Space):
        if isinstance(elem.prev, Str) and elem.prev.text in ['«', '“', '‹']:
            return RawInline('\\thinspace{}', 'tex')
        if isinstance(elem.next, Str):
            if elem.next.text == ':':
                return RawInline('~', 'tex')
            elif elem.next.text in [';', '?', '!', '»', '”', '›']:
                return RawInline('\\thinspace{}', 'tex')


def main(doc=None):
    return run_filter(spaces, doc=doc)


if __name__ == '__main__':
    main()
