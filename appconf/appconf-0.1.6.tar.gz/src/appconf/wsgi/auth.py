# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from jwt import InvalidTokenError
from flask import request, jsonify
from flask_jwt import JWT, JWTError, jwt_required, current_identity

# local imports
from appconf.wsgi import app
from appconf.wsgi.users import User

def user_from_payload(payload):
    return User.query.get(payload['identity'])


jwt = JWT(
    authentication_handler=lambda name, pw: User.authenticate(name, pw),
    identity_handler=user_from_payload
)


def identity_from_token(token):
    try:
        return jwt.jwt_decode_callback(token)['identity']
    except InvalidTokenError:
        return None


@jwt.auth_response_handler
def send_token(access_token, identity):
    return jsonify({'jwt_token': access_token.decode('utf-8')})


@app.after_request
def update_auth(response):
    # Only return refreshed token for API calls.
    if response.content_type == 'application/json':
        auth = request.headers.get('Authorization')
        if auth is not None:
            user_id = identity_from_token(auth.rsplit(maxsplit=1)[-1])

            if user_id is not None:
                token = jwt.jwt_encode_callback(User(id=user_id))
                response.headers['X-JWT-Token'] = token

    return response
