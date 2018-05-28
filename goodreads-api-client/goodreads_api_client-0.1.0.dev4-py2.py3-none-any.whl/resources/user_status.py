# -*- coding: utf-8 -*-
"""Module containing user status resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class UserStatus(Resource):
    resource_name = 'user_status'

    def create(self):
        raise OauthEndpointNotImplemented('user_status.create')

    def destroy(self):
        raise OauthEndpointNotImplemented('user_status.destroy')

    def index(self):
        raise OauthEndpointNotImplemented('user_status.index')

    def show(self, id_: str):
        return self._show_single_resource(id_)
