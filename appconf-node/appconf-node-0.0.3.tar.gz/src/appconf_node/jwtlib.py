# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from collections import OrderedDict
from datetime import datetime, timedelta
from functools import wraps
from logging import getLogger

# 3rd party imports
from jwt import PyJWT, InvalidTokenError as PyJwtInvalidTokenError
from flask import current_app, request


L = getLogger(__name__)
pyjwt = PyJWT()

CONFIG_DEFAULTS = {
    'JWT_HEADER_PREFIX': 'JWT',
    'JWT_TOKEN_TTL': 300,
    'JWT_NOT_BEFORE': 0,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY_CLAIMS': ['signature', 'exp', 'iat', 'nbf'],
    'JWT_REQUIRE_CLAIMS': ['exp', 'iat', 'nbf'],
    'JWT_LEEWAY': 0,
}

AUTH_HEADER_PREFIX = 'JWT'
AUTH_TOKEN_TTL = 300
AUTH_NOT_BEFORE = 0
AUTH_ALGORITHM = 'HS256'
AUTH_VERIFY_CLAIMS = ['signature', 'exp', 'iat', 'nbf']
AUTH_REQUIRE_CLAIMS = ['exp', 'iat', 'nbf']
AUTH_LEEWAY = 0


class JwtError(Exception):
    error = 'Generic Error'
    message = 'Unknown error'
    status = 401

    def __init__(self, message=None, headers=None):
        self.error = self.__class__.error or JwtError.error
        self.message = message or self.__class__.message
        self.status = self.__class__.status
        self.headers = headers

    def __repr__(self):
        return 'JwtError: {}'.format(self.error)

    def __str__(self):
        return 'JwtError: {}: {}'.format(self.error, self.message)


class AuthHeaderMissingError(JwtError):
    error = 'Authorization Header Missing'
    message = "You should set 'Authorization: JWT <token>' header."


class UserNotFoundError(JwtError):
    error = 'User Not Found'
    message = 'User does not exist'


class BadAuthHeaderError(JwtError):
    error = 'Bad Authorization header'
    message = 'Bad Authorization header'


class NotAuthorizedError(JwtError):
    error = "Not Authorized"


class InvalidTokenError(JwtError):
    error = "Not Authorized"


class Jwt(object):
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        for name, value in CONFIG_DEFAULTS.items():
            app.config.setdefault(name, value)

        deserializers = {
            'JWT_TOKEN_TTL': lambda x: timedelta(seconds=x),
            'JWT_NOT_BEFORE': lambda x: timedelta(seconds=x),
        }
        for name, deserialize in deserializers.items():
            app.config[name] = deserialize(app.config[name])

        app.errorhandler(JwtError)(self._flask_exc_handler)

    def authenticate(self, login_required=True):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kw):
                request.user = self.authorize()

                if login_required and request.user is None:
                    raise UserNotFoundError()

                return fn(*args, **kw)

            return wrapper

        return decorator

    def _flask_exc_handler(self, exc):
        from appconf_node.core.api import json_response
        L.error(exc)

        return json_response(exc.status, OrderedDict([
            ('status_code', exc.status),
            ('error', exc.error),
            ('detail', exc.message),
        ]), exc.headers)

    def authorize(self):
        auth = request.headers.get('Authorization')

        if not auth:
            raise AuthHeaderMissingError()

        parts = auth.split()
        if len(parts) != 2 or parts[0] != current_app.config['JWT_HEADER_PREFIX']:
            return None

        try:
            payload = self._decode_token(parts[1])
        except PyJwtInvalidTokenError:
            raise InvalidTokenError()

        return self.user_from_payload(payload)

    def user_payload(self, user):
        raise NotImplemented("user_payload() method must be implemented")

    def user_from_payload(self, payload):
        raise NotImplemented("user_from_payload() method must be implemented")

    def generate_token(self, user):
        secret = current_app.config['SECRET_KEY']
        algo = current_app.config['JWT_ALGORITHM']
        require_claims = current_app.config['JWT_REQUIRE_CLAIMS']

        headers = self.create_headers()
        payload = self.create_payload()
        payload.update(self.user_payload(user))

        missing = frozenset(require_claims) - frozenset(payload.keys())

        if missing:
            raise ValueError("JWT Payload is missing required claims: {}".format(
                ', '.join(missing)
            ))

        return pyjwt.encode(payload, secret, algorithm=algo, headers=headers)

    def create_headers(self):
        return None

    def create_payload(self):
        iat = datetime.utcnow()

        return {
            'iat': iat,
            'exp': iat + current_app.config.get('JWT_TOKEN_TTL'),
            'nbf': iat + current_app.config.get('JWT_NOT_BEFORE')
        }

    def _decode_token(self, token):
        secret = current_app.config['SECRET_KEY']
        algo = current_app.config['JWT_ALGORITHM']
        leeway = current_app.config['JWT_LEEWAY']

        verify_claims = current_app.config['JWT_VERIFY_CLAIMS']
        require_claims = current_app.config['JWT_REQUIRE_CLAIMS']

        opts = {'require_' + claim: True for claim in require_claims}
        opts.update({'verify_' + claim: True for claim in verify_claims})


        return pyjwt.decode(
            token, secret,
            options=opts,
            algorightms=[algo],
            leeway=leeway
        )
