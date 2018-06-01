# -*- coding: utf-8 -*-
"""
Flask implementation for the `RestEndpoint`.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from urllib.parse import urljoin

# 3rd party imports
from flask import request
from flask_jwt import jwt_required
from restible import RestEndpoint

# local imports
from .util import json_response
from appconf_node.users.auth import jwt


class FlaskEndpoint(RestEndpoint):
    """ Endpoint implementation to use in webapp2/AppEngine projects. """
    def __init__(self, res_cls, protected=False):
        super(FlaskEndpoint, self).__init__(res_cls)
        self.protected = protected

    @classmethod
    def extract_request_data(cls, request):
        return request.json

    @classmethod
    def extract_request_query_string(cls, request):
        return request.args

    def dispatch(self, **params):
        """ Override webapp2 dispatcher. """
        request.rest_keys = params

        request.user = jwt.authorize()
        if self.protected and request.user is None:
            return json_response(401, {"detail": "Not authorized"})

        result = self.call_rest_handler(request.method, request)

        return json_response(result.status, result.data, result.headers)

    @classmethod
    def init_app(cls, app, base_url, urlconf):
        cls.endpoints = []

        if not base_url.endswith('/'):
            base_url += '/'

        for entry in urlconf:
            opts = {}

            if len(entry) == 2:
                url, res_cls = entry
            else:
                url, res_cls, opts = entry

            if url.startswith('/'):
                url = url[1:]

            if not url.endswith('/'):
                url += '/'

            endpoint = FlaskEndpoint(res_cls, **opts)
            url_list = urljoin(base_url, url)
            url_detail = urljoin(url_list, '<{name}_pk>/'.format(
                name=endpoint.resource.name
            ))

            app.add_url_rule(
                url_detail,
                endpoint='{}-detail'.format(res_cls.name),
                view_func=endpoint.dispatch,
                methods=['get', 'put', 'delete']
            )
            app.add_url_rule(
                url_list,
                endpoint='{}-list'.format(res_cls.name),
                view_func=endpoint.dispatch,
                methods=['get', 'post']
            )

            cls.endpoints.append(endpoint)
