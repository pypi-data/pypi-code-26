# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from functools import wraps

# 3rd party imports
from jsobj import jsobj


def json_response(code, data, headers=None):
    headers = dict(headers or {})
    headers['Content-Type'] = 'application/json'

    return json.dumps(data), code, headers


class api_route(object):
    ROUTE_ATTR = '__api_route__'

    def __init__(self, methods=None):
        self.meta = jsobj({
            'methods': methods or ['post']
        })

    def __call__(self, fn):
        setattr(fn, self.ROUTE_ATTR, self.meta)
        return fn

    @classmethod
    def get_meta(cls, route):
        return getattr(route, cls.ROUTE_ATTR, {})


class api_action(object):
    ACTION_ATTR = '__api_action__'

    def __init__(self, name=None, generic=False, protected=True):
        self.name = name
        self.generic = generic
        self.protected = protected

    def __call__(self, fn):
        setattr(fn, self.ACTION_ATTR, jsobj({
            'name': self.name or fn.__name__,
            'generic': self.generic,
            'method_name': fn.__name__,
            'protected': self.protected,
        }))
        return fn

    @classmethod
    def is_action(cls, obj):
        return hasattr(obj, cls.ACTION_ATTR)

    @classmethod
    def get_meta(cls, action):
        return getattr(action, cls.ACTION_ATTR, {})

    @classmethod
    def name(cls, action):
        return cls.get_meta(action).get('name')
