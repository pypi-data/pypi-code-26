# -*- coding: utf-8 -*-
"""datatables.py: Django datatableview_advanced_search"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.core.exceptions import FieldError
from django.db.models import Q

from . import compiler

__author__ = 'Steven Klass'
__date__ = '3/1/18 9:22 AM'
__copyright__ = 'Copyright 2018 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class AdvancedSearchDataTable(object):
    """This allows us to use a JIRA like search query"""

    def get_table_map(self):
        """Returns a dictionary of name : model_search_fields"""
        data = {}
        allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ "
        for _, column in self.columns.items():
            label = "".join([x.lower() if x != " " else "_" for x in column.label.lower() if x in allowed])
            data[label] = column.sources
        return data

    def normalize_config_search(self, config, query_config):
        from datatableview.utils import OPTION_NAME_MAP
        return query_config.get(OPTION_NAME_MAP['search'], '').strip()

    def search(self, queryset):
        """ Performs db-only queryset searches. """

        import operator
        from datatableview.utils import split_terms

        table_queries = []

        searches = {}

        # Add per-column searches where necessary
        for name, term in self.config['column_searches'].items():
            for term in set(split_terms(term)):
                columns = searches.setdefault(term, {})
                columns[name] = self.columns[name]

        # Global search terms apply to all columns
        q = None
        try:
            q = self._parse_advanced_search_string(self.config['search'])
            if q is not None:
                return queryset.filter(q)
        except FieldError as err:
            log.debug(err)
        except TypeError as err:
            if self.config['search'] is not None:
                if q is not None:
                    log.warning("Type Error: %s", err)
        except KeyError as err:
            log.debug("Falling back to standard search - %s", err)
            for term in set(split_terms(self.config['search'])):
                # NOTE: Allow global terms to overwrite identical queries that were single-column
                searches[term] = self.columns.copy()
                searches[term].update({None: column for column in self.config['search_fields']})

        for term in searches.keys():
            term_queries = []
            for name, column in searches[term].items():
                if name is None:  # config.search_fields items
                    search_f = self._search_column
                else:
                    search_f = getattr(self, 'search_%s' % (name,), self._search_column)
                q = search_f(column, term)
                if q is not None:
                    term_queries.append(q)
            if term_queries:
                table_queries.append(reduce(operator.or_, term_queries))

        if table_queries:
            q = reduce(operator.and_, table_queries)
            queryset = queryset.filter(q)

        return queryset.distinct()

    def _parse_advanced_search_string(self, search_string):

        try:
            query = compiler(search_string, name_map=self.get_table_map())
            if query is None:
                raise KeyError("Nothing found")
        except Exception as err:
            raise KeyError(err)
        return query

