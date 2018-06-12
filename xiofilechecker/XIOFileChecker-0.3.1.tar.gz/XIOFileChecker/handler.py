#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Class to handle filename for XIOFileChecker.

"""

import re

from ESGConfigParser import ExpressionNotMatch

from utils.constants import *


class Filename(object):
    """
    Handler providing methods to deal with filename patterns.

    """

    def __init__(self, filename, filters):
        # Reformat filename pattern
        self.filename = filename
        self.filename = re.sub('%start_date%', 'startdate', self.filename)
        self.filename = re.sub('%end_date%', 'enddate', self.filename)
        # Add netCDF extension if not exists (e.g., XML patterns) to fit CMIP6_FILENAME_PATTERN
        if not self.filename.endswith('.nc'):
            self.filename += '.nc'
        # Filename attributes as dict(): {institute: 'IPSL', project : 'CMIP5', ...}
        try:
            self.attributes = re.search(CMIP6_FILENAME_PATTERN, self.filename).groupdict()
            for facet in IGNORED_FACETS:
                del (self.attributes[facet])
        except:
            raise ExpressionNotMatch(self.filename, CMIP6_FILENAME_PATTERN)
        # Add boolean to distinguish climatologies
        self.attributes['is_clim'] = 'False'
        if '-clim' in self.filename:
            self.attributes['is_clim'] = 'True'
        # Facet filters as dict(): {institute: 'REGEX', project : 'REGEX', ...}
        self.filters = dict.fromkeys(self.attributes)
        if filters:
            for k in self.filters.keys():
                if k in filters.keys():
                    self.filters[k] = filters[k]

    def get_attrs(self):
        return self.attributes

    def in_scope(self):
        scope = dict.fromkeys(self.attributes)
        for k, v in self.attributes.items():
            if self.filters[k]:
                if re.search(self.filters[k], v):
                    scope[k] = True
                else:
                    scope[k] = False
            else:
                # Default: None = True as no filter
                scope[k] = True
        return True if all(scope.values()) else False

    def mask(self, facets):
        for facet in facets:
            del (self.attributes[facet])
        return self.get_attrs()
