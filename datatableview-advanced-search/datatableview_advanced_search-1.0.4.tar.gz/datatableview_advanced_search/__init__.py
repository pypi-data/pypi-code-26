# -*- coding: utf-8 -*-
"""__init__.py: Django datatableview_advanced_search package container"""

from __future__ import unicode_literals
from __future__ import print_function

from lexer import AdvancedSearchLexer
from parser import AdvancedSearchParser

__author__ = 'Steven Klass'
__version_info__ = (1, 0, 4)
__version__ = '.'.join(map(str, __version_info__))
__date__ = '3/1/18 9:22 AM'
__copyright__ = 'Copyright 2018 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]
__license__ = 'See the file LICENSE.txt for licensing information.'


def compiler(expression, name_map=None, debug=False, log=None):
    adv_parser = AdvancedSearchParser(name_map=name_map, debug=debug, debuglog=log)
    return adv_parser.parse(expression)