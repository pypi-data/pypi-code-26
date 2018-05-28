# -*- coding: utf-8 -*-
"""Module containing author resource class."""

from goodreads_api_client.resources.base import Resource


class Author(Resource):
    resource_name = 'author'

    def books(self, id_: str):
        """List books for an author.

        TODO: Add pagination support
        """
        endpoint = 'author/list/{}'.format(id_)
        res = self._transport.req(endpoint=endpoint)
        return res['author']['books']

    def show(self, id_: str):
        return self._show_single_resource(id_)
