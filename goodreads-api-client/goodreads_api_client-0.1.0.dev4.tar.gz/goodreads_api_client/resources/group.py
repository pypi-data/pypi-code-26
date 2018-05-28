# -*- coding: utf-8 -*-
"""Module containing group resource class."""

from goodreads_api_client.exceptions import OauthEndpointNotImplemented
from goodreads_api_client.resources.base import Resource


class Group(Resource):
    resource_name = 'group'

    def join(self):
        raise OauthEndpointNotImplemented('group.join')

    def list(self, user_id: str, sort: str='title'):
        endpoint = 'group/list/{}'.format(user_id)
        params = {
            'sort': sort,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['groups']

    def members(self, id_: str, sort: str='first_name', q: str=None,
                page: int=1):
        endpoint = 'group/members/{}'.format(id_)
        params = {
            'page': page,
            'sort': sort,
            'q': q,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['group_users']

    def search(self, q: str=None, page: int=1):
        endpoint = 'group/search'
        params = {
            'page': page,
            'q': q,
        }
        res = self._transport.req(endpoint=endpoint, params=params)
        return res['groups']

    def show(self, id_: str):
        return self._show_single_resource(id_)
