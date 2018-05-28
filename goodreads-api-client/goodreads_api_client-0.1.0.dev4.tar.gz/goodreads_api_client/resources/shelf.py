# -*- coding: utf-8 -*-
"""Module containing shelf resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class Shelf(Resource):
    def add_to_shelf(self):
        raise OauthEndpointNotImplemented('shelf.add_to_shelf')

    def add_books_to_shelves(self):
        raise OauthEndpointNotImplemented('shelf.add_books_to_shelves')

    def list(self, user_id: str):
        endpoint = 'shelf/list'
        params = {
            'user_id': user_id,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['shelves']
