# -*- coding: utf-8 -*-
"""Module containing friend resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class Friend(Resource):
    def confirm_recommendation(self):
        raise OauthEndpointNotImplemented('friend.confirm_recommendation')

    def confirm_request(self):
        raise OauthEndpointNotImplemented('friend.confirm_request')

    def requests(self):
        raise OauthEndpointNotImplemented('friend.requests')

    def create(self):
        raise OauthEndpointNotImplemented('friend.create')
