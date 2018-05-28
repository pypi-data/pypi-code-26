# -*- coding: utf-8 -*-
"""Module containing series resource class."""

from goodreads_api_client.resources.base import Resource


class Series(Resource):
    resource_name = 'series'

    def list(self, author_id: str):
        endpoint = 'series/list'
        params = {
            'id': author_id,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['series_works']['series_work']

    def show(self, id_: str):
        return self._show_single_resource(id_)

    def work(self, work_id: str):
        endpoint = 'series/work/{}'.format(work_id)
        res = self._transport.req(endpoint=endpoint)
        return res['series_works']['series_work']
