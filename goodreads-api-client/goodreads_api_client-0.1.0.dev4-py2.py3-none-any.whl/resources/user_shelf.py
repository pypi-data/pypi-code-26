# -*- coding: utf-8 -*-
"""Module containing user shelf resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class UserShelf(Resource):
    def create(self):
        raise OauthEndpointNotImplemented('user_shelf.create')

    def update(self):
        raise OauthEndpointNotImplemented('user_shelf.update')
