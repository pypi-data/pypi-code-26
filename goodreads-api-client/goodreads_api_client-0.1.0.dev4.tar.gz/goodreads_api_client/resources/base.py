# -*- coding: utf-8 -*-
"""Module containing base resource class."""


class Resource(object):
    """Base resource class.

    All Goodreads API resource classes should inherit this.
    """
    resource_name = 'resource'

    def __init__(self, transport=None):
        self._transport = transport

    def _show_single_resource(self, id_: str, uses_oauth: bool=False):
        name = self.__class__.resource_name
        endpoint = '{}/show/{}'.format(name, id_)
        res = self._transport.req(endpoint=endpoint, uses_oauth=uses_oauth)
        return res[name]
