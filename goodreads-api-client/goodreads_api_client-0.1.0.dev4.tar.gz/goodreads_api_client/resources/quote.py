# -*- coding: utf-8 -*-
"""Module containing quote resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class Quote(Resource):
    resource_name = 'quote'

    def create(self):
        raise OauthEndpointNotImplemented('quote.create')
