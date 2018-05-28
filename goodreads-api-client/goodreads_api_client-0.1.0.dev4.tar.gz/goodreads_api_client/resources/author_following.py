# -*- coding: utf-8 -*-
"""Module containing author following resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class AuthorFollowing(Resource):
    def create(self):
        raise OauthEndpointNotImplemented('author.create')

    def destroy(self):
        raise OauthEndpointNotImplemented('author.destroy')

    def show(self, id_: str):
        raise OauthEndpointNotImplemented('author.show')
