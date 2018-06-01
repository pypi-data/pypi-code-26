# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from flask import request

# local imports
from appconf_node.core.api import api_route, json_response
from .models import User
from .auth import jwt


@api_route(methods=['post'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    if not all([username, password, len(data) == 2]):
        return json_response(401, {
            'error': "Bad request",
            'message': "Invalid credentials"
        })

    user = User.authenticate(username, password)

    if user is None:
        return json_response(401, {
            'error': "Bad request",
            'message': "Invalid credentials"
        })

    token = jwt.generate_token(user)

    return json_response(200, {
        'jwt_token': token.decode('utf-8')
    })

