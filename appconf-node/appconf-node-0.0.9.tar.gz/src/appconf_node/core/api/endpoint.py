# -*- coding: utf-8 -*-
"""
Flask implementation for the `RestEndpoint`.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import inspect
from logging import getLogger
from urllib.parse import urljoin

# 3rd party imports
from flask import request
from flask_jwt import jwt_required
from restible import RestEndpoint

# local imports
from .util import api_action, api_route, json_response
from appconf_node.users.auth import jwt


L = getLogger(__name__)


class FlaskEndpoint(RestEndpoint):
    """ Endpoint implementation to use in webapp2/AppEngine projects. """
    def __init__(self, res_cls, protected=False):
        super(FlaskEndpoint, self).__init__(res_cls)
        self.protected = protected
        self.actions = self._get_resource_actions(self.resource)

    @classmethod
    def extract_request_data(cls, request):
        return request.json

    @classmethod
    def extract_request_query_string(cls, request):
        return request.args

    def _get_resource_actions(self, resource):
        actions = []
        for name, method in inspect.getmembers(resource, inspect.ismethod):
            if api_action.is_action(method):
                actions.append(method)

        return actions

    def dispatch(self, **params):
        """ Override webapp2 dispatcher. """
        request.rest_keys = params

        request.user = jwt.authorize()
        if self.protected and request.user is None:
            return json_response(401, {"detail": "Not authorized"})

        result = self.call_rest_handler(request.method, request)

        return json_response(result.status, result.data, result.headers)

    def find_action(self, name, generic):
        for action in self.actions:
            meta = api_action.get_meta(action)

            if meta.name == name and meta.generic == generic:
                return action

        return None

    def dispatch_action(self, name, generic, **params):
        """ Override webapp2 dispatcher. """
        request.rest_keys = params

        # TODO: search for action by action name (meta), not method name
        action = self.find_action(name, generic)
        if action is None:
            return json_response(404, {
                'detail': "action {} not found on {}".format(
                    name, self.resource.name
                )
            })

        meta = api_action.get_meta(action)

        try:
            request.user = jwt.authorize()
        except jwt.Error:
            request.user = None

        if meta.protected and request.user is None:
            return json_response(401, {"detail": "Not authorized"})

        action_params = {'payload': request.json}

        if not meta.generic:
            obj = self.resource.get_requested(request)

            if obj is None:
                pk = self.resource.get_pk(request)
                return json_response(404, {
                    'detail': "{} #{} not found".format(self.resource.name, pk)
                })

            action_params['obj'] = obj

        L.info("Calling action {}".format(action))
        result = action(**action_params)
        result = self.process_result(result, 200)

        return json_response(result.status, result.data, result.headers)

    @classmethod
    def init_app(cls, app, resources=None, routes=None):
        resources = resources or []
        routes = routes or []
        cls.endpoints = []

        for entry in resources:
            opts = {}

            if len(entry) == 2:
                url, res_cls = entry
            else:
                url, res_cls, opts = entry

            if not url.endswith('/'):
                url += '/'

            endpoint = FlaskEndpoint(res_cls, **opts)
            endpoint._register_routes(app, url)

            cls.endpoints.append(endpoint)

        for url, route in routes:
            meta = api_route.get_meta(route)
            app.add_url_rule(url[:-1], view_func=route, **meta)
            app.add_url_rule(url, view_func=route, **meta)

    def _register_routes(self, app, url):
        """ Register all routes for the current endpoint in the flask app. """
        url_list = url
        url_item = urljoin(url, '<{name}_pk>/'.format(
            name=self.resource.name
        ))

        # actions
        for action in self.actions:
            meta = api_action.get_meta(action)

            action_route = dict(
                endpoint='{}-{}'.format(self.resource.name, meta.name),
                defaults={
                    'name': meta.name,
                    'generic': meta.generic,
                },
                view_func=self.dispatch_action,
                methods=['post']
            )

            base_url = url_list if meta.generic else url_item
            url_action = urljoin(base_url, meta.name + '/')

            # Add without and with slash
            app.add_url_rule(url_action[:-1], **action_route)
            app.add_url_rule(url_action, **action_route)

        item_route = dict(
            endpoint='{}-item'.format(self.resource.name),
            view_func=self.dispatch,
            methods=['get', 'put', 'delete']
        )
        list_route = dict(
            endpoint='{}-list'.format(self.resource.name),
            view_func=self.dispatch,
            methods=['get', 'post']
        )

        # Add without and with slash
        app.add_url_rule(url_item[:-1], **item_route)
        app.add_url_rule(url_item, **item_route)

        # Add without and with slash
        app.add_url_rule(url_list[:-1], **list_route)
        app.add_url_rule(url_list, **list_route)
