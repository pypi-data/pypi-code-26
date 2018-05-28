# -*- coding: utf-8 -*-
"""
goodreads_api_client.transport
~~~~~

Contains transport underlying all requests made to the Goodreads API.
"""

from collections import OrderedDict
import json
import os
import webbrowser

from rauth.service import OAuth1Service, OAuth1Session
import requests
import xmltodict

credentials_file_path = \
    os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.pardir,
            'client_id.json',
        )
    )


class Transport(object):
    """Makes requests to Goodreads API and applies transform to response."""

    def __init__(self, developer_key: str, developer_secret: str=None,
                 base_url: str=None):
        """Initialize with credentials.

        :param str developer_key: Your Goodreads developer key. Find or
            generate one here <https://goodreads.com/api/keys>
        :param str developer_secret: Your Goodreads developer secret
        :param str/None base_url: Base URL of the Goodreads API.
            Defaults to https://goodreads.com.
        """
        if base_url is None:
            self.base_url = 'http://www.goodreads.com'
        else:
            self.base_url = base_url

        self._developer_key = developer_key
        self._developer_secret = developer_secret
        self._gr = None
        self._request_token = None
        self._request_token_secret = None
        self._session = None

    def authorize(self):
        if self._session is not None:
            return

        self._request_token, self._request_token_secret = \
            self.gr.get_request_token(header_auth=True)

        authorize_url = self._gr.get_authorize_url(self._request_token)
        webbrowser.open(authorize_url)

    @property
    def session(self):
        if self._session is not None:
            return self._session

        credentials = Transport.read_credentials()

        if credentials:
            self._session = OAuth1Session(
                consumer_key=self._developer_key,
                consumer_secret=self._developer_secret,
                access_token=credentials['access_token'],
                access_token_secret=credentials['access_token_secret'],
            )
        else:
            self._session = self.gr.get_auth_session(
                self._request_token, self._request_token_secret)
            self._write_credentials()

        return self._session

    def is_using_session(self) -> bool:
        return self._session is not None

    @property
    def gr(self):
        if self._gr is not None:
            return self._gr

        self._gr = OAuth1Service(
            consumer_key=self._developer_key,
            consumer_secret=self._developer_secret,
            name='goodreads',
            request_token_url=self.request_token_url,
            authorize_url=self.authorize_url,
            access_token_url=self.access_token_url,
            base_url=self.base_url,
        )

        return self._gr

    @property
    def authorize_url(self):
        return '{}/oauth/authorize'.format(self.base_url)

    @property
    def access_token_url(self):
        return '{}/oauth/access_token'.format(self.base_url)

    @property
    def request_token_url(self):
        return '{}/oauth/request_token'.format(self.base_url)

    def _req(self, method: str='GET', endpoint: str=None, params: dict=None,
             data: dict=None, uses_oauth: bool=False):
        if params is None:
            params = {}

        fetch = self.session.request if uses_oauth else requests.request

        res = fetch(
            method=method,
            url='{}/{}'.format(self.base_url, endpoint),
            params={
                'format': 'xml',
                'key': self._developer_key,
                **params
            },
            data=data
        )

        res.raise_for_status()
        return res

    @staticmethod
    def _transform_res(res, transform: str='xml'):
        if transform == 'xml':
            content = xmltodict.parse(res.text)
            return content['GoodreadsResponse']
        if transform == 'json':
            content = json.loads(res.text)
            # This is just for consistency of return values across
            # different methods in this class - the ordering is not meaningful
            return OrderedDict(content.items())
        return res.text

    def req(self, method: str='GET', endpoint: str=None, params: dict=None,
            data: dict=None, transform: str='xml', uses_oauth: bool=False):
        res = self._req(method, endpoint, params, data, uses_oauth)
        return Transport._transform_res(res, transform)

    def _write_credentials(self):
        blob = {
            'developer_key': self._developer_key,
            'developer_secret': self._developer_secret,
            'access_token': self.session.access_token,
            'access_token_secret': self.session.access_token_secret,
        }

        with open(credentials_file_path, 'w+') as creds_file:
            json.dump(blob, creds_file, sort_keys=True, indent=4)

    @staticmethod
    def read_credentials():
        if not os.path.exists(credentials_file_path):
            return None

        with open(credentials_file_path, 'r') as creds_file:
            return json.loads(creds_file.read())
