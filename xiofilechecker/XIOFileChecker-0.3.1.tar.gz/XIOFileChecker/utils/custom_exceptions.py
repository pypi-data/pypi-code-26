#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Custom exceptions used in this module.

"""

from constants import RUN_CARD, CONF_CARD


class InvalidFilters(Exception):
    """
    Raised when a regular expression resolution failed.

    """

    def __init__(self, filters, facets):
        self.msg = "Invalid filter(s)"
        self.msg += "\n<unrecognized_filters: '{}'>".format(', '.join(filters))
        self.msg += "\n<available_filters: '{}'>".format(', '.join(facets))
        super(self.__class__, self).__init__(self.msg)


class NoFileFound(Exception):
    """
    Raised when no netCDF files have been found.

    """

    def __init__(self):
        self.msg = "No netCDF files found."
        super(self.__class__, self).__init__(self.msg)


class NoPatternFound(Exception):
    """
    Raised when no file patterns found in filedef.

    """

    def __init__(self):
        self.msg = "No file patterns found"
        super(self.__class__, self).__init__(self.msg)


class NoRunCardFound(Exception):
    """
    Raised when no file patterns found in filedef.

    """

    def __init__(self, path):
        self.msg = "No {} found".format(RUN_CARD)
        self.msg += "\n<path: '{}'>".format(path)
        super(self.__class__, self).__init__(self.msg)


class NoConfigCardFound(Exception):
    """
    Raised when no file patterns found in filedef.

    """

    def __init__(self, path):
        self.msg = "No {} found".format(CONF_CARD)
        self.msg += "\n<path: '{}'>".format(path)
        super(self.__class__, self).__init__(self.msg)
