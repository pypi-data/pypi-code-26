# -*- coding: utf-8 -*-
"""jira_lex.py: Django datatableview_advanced_search"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

import sys

import operator

from lexer import AdvancedSearchLexer

__author__ = 'Steven Klass'
__date__ = '2/28/18 9:20 AM'
__copyright__ = 'Copyright 2018 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

compa2lookup = {
    '=': 'exact',
    '~=': 'contains',
    '>': 'gt',
    '>=': 'gte',
    '<': 'lt',
    '<=': 'lte',
}


class AdvancedSearchParser(object):
    tokens = AdvancedSearchLexer.tokens

    def __init__(self, **kwargs):
        import ply.yacc as yacc
        self.name_map = kwargs.pop('name_map', {})
        self.lexer = AdvancedSearchLexer(**kwargs).lexer
        self.parser = yacc.yacc(module=self, **kwargs)

    def p_expression_paren(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]


    def p_expression_compare(self, p):
        """expression : variable COMPARE value"""

        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "
        field = "".join([x.lower() if x != " " else "_" for x in p[1].lower() if x in allowed])
        sources = self.name_map.get(field, [p[1]])
        if not isinstance(sources, list):
            sources = [sources]

        from django.db.models import Q

        lookup = compa2lookup[p[2]]
        query = []
        for source in sources:
            if lookup:
                source = '%s__%s' % (source, lookup)
                query.append(Q(**{str((source)): p[3]}))

        if len(query) > 1:
            p[0] = reduce(operator.or_, query)
        else:
            p[0] = query[0]

    def p_expression_in(self, p):
        """expression : variable IN list"""
        from django.db.models import Q
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "
        field = "".join([x.lower() if x != " " else "_" for x in p[1].lower() if x in allowed])
        sources = self.name_map.get(field, [p[1]])
        if not isinstance(sources, list):
            sources = [sources]

        query = []
        for source in sources:
            source = '%s__in' % (source)
            query.append(Q(**{str((source)): p[3]}))

        if len(query) > 1:
            p[0] = reduce(operator.or_, query)
        else:
            p[0] = query[0]

    def p_list(self, p):
        """list : LBRACK list_vals RBRACK"""
        p[0] = p[2]


    def p_list_vals(self, p):
        """list_vals : value COMMA value
                     | list_vals COMMA value"""
        if isinstance(p[1], list):
            if isinstance(p[3], list):
                p[0] = p[1] + p[3]
            else:
                p[0] = p[1] + [p[3]]
        else:
            if isinstance(p[3], list):
                p[0] = [p[1]] + p[3]
            else:
                p[0] = [p[1]] + [p[3]]


    def p_expression_not(self, p):
        """expression : NOT expression"""
        p[0] = ~ p[2]


    def p_expression_and(self, p):
        """expression : expression AND expression"""
        p[0] = p[1] & p[3]


    def p_expression_or(self, p):
        """expression : expression OR expression"""
        p[0] = p[1] | p[3]


    precedence = (
        ('left', 'AND'),
        ('left', 'OR'),
        ('right', 'NOT'),
    )


    def p_value(self, p):
        '''value : variable
                 | number
                 | DATE'''
        p[0] = p[1]


    def p_variable(self, p):
        '''variable : WORD
                    | SINGLE_QUOTE_WORD
                    | DOUBLE_QUOTE_WORD'''
        p[0] = p[1]


    def p_number(self, p):
        '''number : INT
                  | FLOAT'''
        p[0] = p[1]


    def p_error(self, p):
        if p:
            log.info("Parsing error around token: '%s'" % p.value)
        else:
            log.debug("Parsing error: unexpected end of expression")

    def parse(self, text):
        return self.parser.parse(text, self.lexer)


def main(args):
    """Main - $<description>$"""
    logging.basicConfig(
        level=logging.DEBUG, datefmt="%H:%M:%S", stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(filename)s] (%(name)s) %(message)s")

    # Test it out
    data = '''
    (foo='bar\'s' AND x=1) OR (ya IN [2, 3, -3.5]) AND datestamp >= 1/25/2018 AND X="THe OTH3R"
    '''

    name_map = {'foo': ['foo__name', 'foo__id']}

    m = AdvancedSearchParser(name_map=name_map)
    print(m.parse(data)) # Test it


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="$<description>$")
    sys.exit(main(parser.parse_args()))
