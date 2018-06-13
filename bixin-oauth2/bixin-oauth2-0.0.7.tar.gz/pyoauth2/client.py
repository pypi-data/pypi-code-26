# -*- coding: utf-8 -*-

from .libs.auth_code import AuthCode
from .libs.access_token import AccessToken
from .libs.request import Request
from .libs.connection import Connection

SITE_URL = 'https://bixin.im'
AUTHORIZE_URL = '/auth/oauth/authorize/'
TOKEN_URL = '/auth/oauth/get_token/'
RESOURCE_URL = '/api/v1/user/profile'

class Client(object):

    def __init__(self, client_id, client_secret, **opts):
        self.id = client_id
        self.secret = client_secret
        self.site = opts.pop('site', SITE_URL)
        self.opts = {'authorize_url': AUTHORIZE_URL,
                     'token_url': TOKEN_URL,
                     'resource_url': RESOURCE_URL,
                     'connection_opts': {},
                     'raise_errors': True, }
        self.opts.update(opts)

    def __repr__(self):
        return '<OAuth2 Client>'

    def authorize_url(self, params={}):
        return Connection.build_url(self.site, path=self.opts['authorize_url'], params=params)

    def token_url(self, params={}):
        return Connection.build_url(self.site, path=self.opts['token_url'], params=params)

    def resource_url(self, params={}):
        return Connection.build_url(self.site, path=self.opts['resource_url'], params=params)

    def request(self, method, uri, **opts):
        uri = Connection.build_url(self.site, path=uri)
        response = Request(method, uri, **opts).request()
        return response

    def get_token(self, **opts):
        self.response = self.request('POST', self.token_url(), **opts)
        opts.update(self.response.parsed)
        self.token = AccessToken.from_hash(self, **opts).token
        return self.token

    def get_user_profile(self, **opts):
        params = {'access_token': self.token}
        opts.update(params)
        self.response = self.request('GET', self.resource_url(), **opts)
        return self.response.parsed

    @property
    def auth_code(self):
        return AuthCode(self)
