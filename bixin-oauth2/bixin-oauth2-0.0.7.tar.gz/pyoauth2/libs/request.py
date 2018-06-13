# -*- coding: utf-8 -*-
import json
import requests

from .response import Response
from .errors import HaobtcOauthError


class Request(object):

    def __init__(self, method, uri,
                 headers=None,
                 files=None,
                 timeout=None,
                 allow_redirects=True,
                 proxies=None,
                 hooks=None,
                 stream=None,
                 verify=None,
                 cert=None,
                 parse='json',
                 **opts):
        self.method = method
        self.uri = uri
        self.headers = headers or {}
        self.files = files
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.proxies = proxies
        self.hooks = hooks
        self.stream = stream
        self.verify = verify
        self.cert = cert
        self.parse = parse
        if self.headers.get('content-type') == 'application/json':
            self.opts = json.dumps(opts)
        else:
            self.opts = opts

    def __repr__(self):
        return '<OAuth2 Request>'

    def request(self):
        data = params = None
        if self.method in ('POST', 'PUT'):
            data = self.opts
        else:
            params = self.opts
        response = requests.request(self.method, self.uri,
                                    params=params,
                                    data=data,
                                    headers=self.headers,
                                    files=self.files,
                                    timeout=self.timeout,
                                    allow_redirects=self.allow_redirects,
                                    proxies=self.proxies,
                                    hooks=self.hooks,
                                    stream=self.stream,
                                    verify=self.verify,
                                    cert=self.cert)

        response = Response(response, parse=self.parse)
        body = response.parsed
        if body['ok']:
            return response
        else:
            raise HaobtcOauthError(body['code'], body['message'])

