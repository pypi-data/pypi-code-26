# -*- coding: utf-8 -*-
"""
Various validation helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from functools import wraps

# 3rd party imports
from jsonschema import validate, ValidationError


class validate_json(object):
    """ View decorator for validating JSON request against a schema

    Will return HTTP 400 if the request body doesn't match the schema.
    """
    def __init__(self, schema):     # pylint: disable=missing-docstring
        self.schema = schema

    def __call__(self, fn):
        # pylint: disable=missing-docstring
        @wraps(fn)
        def action_handler(handler, *args, **kwargs):
            try:
                handler.request.data = json.loads(handler.request.body)
                validate(handler.request.data, self.schema)

            except ValidationError as ex:
                return handler.respond(400, {
                    'msg': ex.message,
                    "detail": str(ex)
                })

            return fn(handler, *args, **kwargs)

        return action_handler
