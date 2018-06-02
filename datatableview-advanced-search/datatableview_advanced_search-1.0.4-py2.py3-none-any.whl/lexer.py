# -*- coding: utf-8 -*-
"""jira_lex.py: Django datatableview_advanced_search"""

from __future__ import unicode_literals
from __future__ import print_function

import sys
import logging
from datetime import date


__author__ = 'Steven Klass'
__date__ = '2/28/18 9:20 AM'
__copyright__ = 'Copyright 2018 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


reserved = {
    'IN': 'IN',
    'AND': 'AND',
    'OR': 'OR',
    'NOT': 'NOT'
}

class AdvancedSearchLexer(object):

    tokens = ['WORD', 'SINGLE_QUOTE_WORD', 'DOUBLE_QUOTE_WORD', 'DATE', 'FLOAT', 'INT',
              'COMPARE', 'LBRACK', 'RBRACK', 'COMMA', 'LPAREN', 'RPAREN'] + reserved.values()

    t_COMPARE = r'!?=|[<>]=?|~='
    t_COMMA = r','
    t_LBRACK = r'\['
    t_RBRACK = r'\]'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def __init__(self, **kwargs):
        import ply.lex as lex
        self.lexer = lex.lex(module=self, **kwargs)
        self.lexer.linestart = 0

    def __iter__(self):
        return iter(self.lexer)

    # dates are in the following format: /mm/dd/yyyy
    def t_DATE(self, t):
        r'(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})'
        day = int(t.lexer.lexmatch.group('day'))
        month = int(t.lexer.lexmatch.group('month'))
        year = int(t.lexer.lexmatch.group('year'))
        t.value = date(year, month, day)
        return t

    def t_SINGLE_QUOTE_WORD(self, t):
        r"(')(?P<word>[a-zA-Z_0-9][a-zA-Z_0-9:\.\\'\" ]*)(')"
        t.value = t.lexer.lexmatch.group('word')
        return t

    def t_DOUBLE_QUOTE_WORD(self, t):
        r'(")(?P<word>[a-zA-Z_0-9][a-zA-Z_0-9:\.\\"\' ]*)(")'
        t.value = t.lexer.lexmatch.group('word')
        return t

    def t_WORD(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9:\.]*|\d+[a-zA-Z_:]+[a-zA-Z_0-9:\.]*'
        # This allows for words beginning with numbers but you must have a letter in there somewhere
        t.type = reserved.get(t.value, 'WORD')  # Check for reserved words
        return t

    def t_FLOAT(self, t):
        r'[-+]?\d+\.(\d+)?([eE][-+]?\d+)?'
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r'[-+]?\d+'
        t.value = int(t.value)
        return t

    # A string containing ignored characters (spaces and tabs)
    t_ignore = " \t"


    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)


    def t_error(self, t):
        log.error("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Test it output
    def test(self, data, print_output=True):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            if print_output:
                print(tok)
        return True


def main(args):
    """Main - $<description>$"""
    logging.basicConfig(
        level=logging.DEBUG, datefmt="%H:%M:%S", stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(filename)s] (%(name)s) %(message)s")

    # Test it out
    data = '''
    (foo='bar\'s' AND x=1) OR (y NOT IN [2, 3, -3.5]) AND datestamp >= 1/25/2018 AND X="THe OTH3R"
    '''

    m = AdvancedSearchLexer()
    m.test(data)  # Test it


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="$<description>$")
    sys.exit(main(parser.parse_args()))
