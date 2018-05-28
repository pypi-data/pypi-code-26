# -*- coding: utf-8 -*-
"""Module containing read status resource class."""

from goodreads_api_client.resources.base import Resource


class ReadStatus(Resource):
    resource_name = 'read_status'

    def show(self, id_: str):
        endpoint = 'read_statuses/{}'.format(id_)
        res = self._transport.req(endpoint=endpoint)
        return res['read_status']
