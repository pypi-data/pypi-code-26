# -*- coding: utf-8 -*-
import time
from .utils import urlparse


class AccessToken(object):

    def __init__(self, client, token, **opts):
        self.client = client
        self.token = token

        for attr in ['refresh_token', 'expires_in', 'expires_at']:
            if attr in opts.keys():
                setattr(self, attr, opts.pop(attr))

        self.params = opts

    def __repr__(self):
        return '<OAuth2 AccessToken>'

    @classmethod
    def from_hash(cls, client, **opts):
        return cls(client, opts.pop('access_token', ''), **opts)

    @classmethod
    def from_kvform(cls, client, kvform):
        opts = dict(urlparse.parse_qsl(kvform))
        return cls(client, opts.pop('access_token', ''), **opts)

    def refresh(self, **opts):
        if not getattr(self, 'refresh_token', None):
            raise 'A refresh_token is not available'

        opts = {'client_id': self.client.id,
                'client_secret': self.client.secret,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token',
                }
        new_token = self.client.get_token(**opts)
        return new_token
