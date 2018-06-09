# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth


class BaseAPI(object):

    def __init__(self, session, url_prefix):
        self.session = session
        self.url_prefix = url_prefix

    def request(self, method, item_id=None, **kwargs):
        if item_id is None:
            url = self.url_prefix
        else:
            url = self.url_prefix + str(item_id)
        return self.session.request(method, url, **kwargs)

    def get(self, item_id=None, **kwargs):
        return self.request('get', item_id, **kwargs)

    def post(self, item_id=None, **kwargs):
        return self.request('post', item_id, **kwargs)

    def put(self, item_id=None, **kwargs):
        return self.request('put', item_id, **kwargs)

    def patch(self, item_id=None, **kwargs):
        return self.request('patch', item_id, **kwargs)

    def delete(self, item_id=None, **kwargs):
        return self.request('delete', item_id, **kwargs)


class RestClient(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.base_url = app.config['REST_CLIENT_BASE_URL']
        username = app.config['REST_CLIENT_USERNAME']
        password = app.config['REST_CLIENT_PASSWORD']
        verify = app.config['REST_CLIENT_VERIFY']

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        if verify:
            self.session.verify = verify

    def request(self, method, path, **kwargs):
        url = self.base_url + path
        return self.session.request(method, url, **kwargs)

    def get_api(self, path_prefix):
        url_prefix = self.base_url + path_prefix
        return BaseAPI(self.session, url_prefix)
