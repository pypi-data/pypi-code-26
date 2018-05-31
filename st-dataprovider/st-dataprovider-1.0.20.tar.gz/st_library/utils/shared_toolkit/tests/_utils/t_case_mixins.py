import os

import requests
import requests_mock
from urlobject import URLObject

from ...api_client import resources


class InstantiateMixin(object):
    FIXTURE_SIMPLE_RESPONSE = 'simple_response.json'
    FIXTURE_REFRESH_TOKEN = 'refresh_token.json'
    FIXTURE_PUBLIC_KEY = 'fake_public_key'
    FIXTURE_ENCODED_TOKEN = 'fake_encoded_token'
    FIXTURE_ACCESS_TOKEN = 'access_token.json'

    @classmethod
    def setUpClass(cls):
        super(InstantiateMixin, cls).setUpClass()
        cls._dirname = os.path.dirname(os.path.dirname(__file__))
        fixture_names = [
            cls.FIXTURE_SIMPLE_RESPONSE,
            cls.FIXTURE_REFRESH_TOKEN,
            cls.FIXTURE_PUBLIC_KEY,
            cls.FIXTURE_ENCODED_TOKEN,
            cls.FIXTURE_ACCESS_TOKEN
        ]
        cls.fixtures = {name: cls._get_fixture(name) for name in fixture_names}

        cls.url1 = URLObject('http://example.com')
        cls.path1 = 'simple'
        cls.url1_path1 = cls.url1.add_path(cls.path1)

        cls.url_refresh = URLObject(resources.UAA_SERVICE_ENDPOINT)
        cls.path_refresh = 'api-keys/123'
        cls.url_refresh_path_refresh = cls.url_refresh.add_path(cls.path_refresh)

        cls.url_public_key = URLObject(resources.JWTKEY_ENDPOINT)
        cls.path_public_key = 'token_publickey'
        cls.url_public_key_path_public_key = cls.url_public_key.add_path(cls.path_public_key)

        cls.url_oauth = URLObject(resources.OAUTH_SERVICE_ENDPOINT)
        cls.path_oauth_token = 'token'
        cls.url_oauth_path_oauth_token = cls.url_oauth.add_path(cls.path_oauth_token)

        cls.url_using_sec_token = URLObject('http://example.com')
        cls.path_using_sec_token = 'sec'
        cls.url_using_sec_token_path_using_sec_token = cls.url_using_sec_token.add_path(cls.path_using_sec_token)

    @classmethod
    def _get_fixture(cls, fixture_name):
        path = os.path.join(cls._dirname, '_fixtures', fixture_name)
        with open(path) as f:
            return f.read()


class ApiClientSharedTestsMixin(object):
    """
    This is a test for core functionality which shouldn't be broken by mixins
    """
    def test_request_simple(self):
        with requests_mock.mock() as m:
            m.get(self.url1_path1, text=self.fixtures[self.FIXTURE_SIMPLE_RESPONSE], status_code=200)
            r = self.api_client.request(self.api_client.GET, self.path1, base=self.url1)
            self.assertEqual('ok', r['status'])

    def test_request_simple_error(self):
        with requests_mock.mock() as m:
            m.get(self.url1_path1, text=self.fixtures[self.FIXTURE_SIMPLE_RESPONSE], status_code=400)
            with self.assertRaises(self.api_client.HttpError) as context:
                self.api_client.request(self.api_client.GET, self.path1, base=self.url1)

    def test_request_performing_error(self):
        with requests_mock.mock() as m:
            m.get(self.url1_path1,
                  exc=requests.exceptions.RequestException)

            with self.assertRaises(self.api_client.RequestError):
                self.api_client.request(self.api_client.GET, self.path1, base=self.url1)
