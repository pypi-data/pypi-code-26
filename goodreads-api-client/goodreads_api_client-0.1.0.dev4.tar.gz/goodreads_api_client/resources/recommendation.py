# -*- coding: utf-8 -*-
"""Module containing recommendation resource class."""

from goodreads_api_client.resources.base import Resource


class Recommendation(Resource):
    def show(self, id_: str):
        endpoint = 'recommendations/{}'.format(id_)
        res = self._transport.req(endpoint=endpoint, uses_oauth=True)
        return res['recommendation']
