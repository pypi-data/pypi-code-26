# -*- coding: utf-8 -*-
"""Module containing owned book resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class OwnedBook(Resource):
    def create(self):
        raise OauthEndpointNotImplemented('owned_book.compare')

    def destroy(self):
        raise OauthEndpointNotImplemented('owned_book.destroy')

    def list(self):
        raise OauthEndpointNotImplemented('owned_book.list')

    def show(self):
        raise OauthEndpointNotImplemented('owned_book.show')

    def update(self):
        raise OauthEndpointNotImplemented('owned_book.update')
