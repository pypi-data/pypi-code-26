# -*- coding: utf-8 -*-
"""Module containing comment resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class Comment(Resource):
    def create(self):
        raise OauthEndpointNotImplemented('comment.create')

    def list(self, id_: str, resource_type: str='review'):
        endpoint = 'comment'
        params = {
            'id': id_,
            'type': resource_type,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['comments']
