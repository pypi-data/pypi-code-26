# -*- coding: utf-8 -*-
"""Module containing topic resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class Topic(Resource):
    resource_name = 'topic'

    def create(self):
        raise OauthEndpointNotImplemented('topic.create')

    def group_folder(self, id_: str):
        endpoint = 'topic/group_folder/{}'.format(id_)
        res = self._transport.req(endpoint=endpoint)
        return res['group_folder']

    def show(self, id_: str):
        return self._show_single_resource(id_)

    def unread_group(self):
        raise OauthEndpointNotImplemented('topic.unread_group')
