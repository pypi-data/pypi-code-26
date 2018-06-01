# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from functools import wraps


def json_response(code, data, headers=None):
    headers = dict(headers or {})
    headers['Content-Type'] = 'application/json'

    return json.dumps(data), code, headers


class api_route(object):
    ROUTE_ATTR = '__api_route__'

    def __init__(self, methods=None):
        self.meta = {
            'methods': methods or ['post']
        }

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kw):
            return fn(*args, **kw)

        wrapper.__api_route__ = self.meta
        return wrapper

    @classmethod
    def get_meta(cls, route):
        return getattr(route, cls.ROUTE_ATTR, {})

