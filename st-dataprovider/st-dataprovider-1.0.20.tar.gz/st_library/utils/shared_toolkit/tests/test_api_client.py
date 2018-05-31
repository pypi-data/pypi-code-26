import unittest
from datetime import datetime
from mock import patch

import requests_mock
from pytz import UTC

from ._utils.mock_classes import MockApiClient, MockRefreshTokenApiClient, MockAccessTokenApiClient
from ._utils.t_case_mixins import InstantiateMixin, ApiClientSharedTestsMixin


class MustBeGottenFromCache(Exception):
    pass


class TestBaseApiClient(InstantiateMixin, ApiClientSharedTestsMixin, unittest.TestCase):
    def setUp(self):
        self.api_client = MockApiClient()

    def test_request_other_errors(self):
        with requests_mock.mock() as m:
            with self.assertRaises(AssertionError):
                self.api_client.request(self.api_client.GET, self.path1, base=self.url1, sec_id_for_special_token='foo')


class TestSecRefreshTokenMixin(InstantiateMixin, ApiClientSharedTestsMixin, unittest.TestCase):
    def setUp(self):
        self.api_client = MockRefreshTokenApiClient()

    def test_get_sec_refresh_token(self):
        with requests_mock.mock() as m:
            m.get(self.url_refresh_path_refresh, text=self.fixtures[self.FIXTURE_REFRESH_TOKEN], status_code=200)
            refresh_token = self.api_client.get_sec_refresh_token('123')
            self.assertEqual('bar', refresh_token)
            self.assertEqual('bar', self.api_client._get_cache_sec_refresh_token('123'), 'Refresh token must be cached')
        # Now refresh token must be gotten from cache
        with requests_mock.mock() as m:
            m.get(self.url_refresh_path_refresh, exc=MustBeGottenFromCache)
            refresh_token = self.api_client.get_sec_refresh_token('123')
            self.assertEqual('bar', refresh_token)


class RetryEmulationApiClient(MockAccessTokenApiClient):
    def __init__(self, request_mock_callback, *args, **kwargs):
        self.request_mock_callback = request_mock_callback
        super(RetryEmulationApiClient, self).__init__(*args, **kwargs)

    def _retry_occurred(self):
        """
        For emulation the situation when token was expired while request is processing,
        we need to make a new mock with good response
        """
        self.request_mock_callback()


class TestSecAccessTokenMixin(InstantiateMixin, ApiClientSharedTestsMixin, unittest.TestCase):
    def setUp(self):
        self.api_client = MockAccessTokenApiClient()

    def test_get_public_key(self):
        with requests_mock.mock() as m:
            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)
            public_key = self.api_client.get_public_key()
            self.assertEqual(fixture_public_key, public_key)
            self.assertEqual(fixture_public_key, self.api_client._get_cache_public_key(), 'Public key must be cached')
        # Now refresh token must be gotten from cache
        with requests_mock.mock() as m:
            m.get(self.url_public_key_path_public_key, exc=MustBeGottenFromCache)
            public_key = self.api_client.get_public_key()
            self.assertEqual(fixture_public_key, public_key)

    def test_parse_access_token_expiration(self):
        with requests_mock.mock() as m:
            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)
            expiration = self.api_client.parse_access_token_expiration(self.fixtures[self.FIXTURE_ENCODED_TOKEN])
            self.assertEqual(datetime(year=2018, month=3, day=22, hour=10, minute=4, second=5, tzinfo=UTC), expiration)

    def test_is_sec_access_token_expired(self):
        self.assertTrue(self.api_client._is_sec_access_token_expired('123'),
                        'Must be expired because empty cache')

        # for example token expiration is set (do it next line)
        self.api_client.\
            _set_cache_sec_access_token_expiration('123',
                                                   datetime(year=2018, month=3, day=22,
                                                            hour=10, minute=4, second=5, tzinfo=UTC))

        with requests_mock.mock() as m:
            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=3, second=0, tzinfo=UTC)
                self.assertFalse(self.api_client._is_sec_access_token_expired('123'),
                                 'Must not be expired because is about minute difference')

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=4, second=0, tzinfo=UTC)

                self.assertTrue(self.api_client._is_sec_access_token_expired('123'),
                                'Must be expired because is about 5 seconds difference')

    def test_get_sec_access_token(self):
        with requests_mock.mock() as m:
            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)
            m.post(self.url_oauth_path_oauth_token, text=self.fixtures[self.FIXTURE_ACCESS_TOKEN], status_code=200)

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                # (expired)
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=4, second=0, tzinfo=UTC)

                access_token = self.api_client.get_sec_access_token('123')
                self.assertEqual(self.fixtures[self.FIXTURE_ENCODED_TOKEN], access_token)

                cached_expiration = self.api_client._get_cache_sec_access_token_expiration('123')
                self.assertEqual(datetime(year=2018, month=3, day=22, hour=10, minute=4, second=5, tzinfo=UTC),
                                 cached_expiration)

                cached_access_token = self.api_client._get_cache_sec_access_token('123')
                self.assertEqual(self.fixtures[self.FIXTURE_ENCODED_TOKEN], cached_access_token)

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                # (not expired)
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=3, second=0, tzinfo=UTC)
                m.post(self.url_oauth_path_oauth_token, exc=MustBeGottenFromCache)
                access_token = self.api_client.get_sec_access_token('123')
                self.assertEqual(self.fixtures[self.FIXTURE_ENCODED_TOKEN], access_token)

    def test_full_cycle_request(self):
        with requests_mock.mock() as m:
            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)
            m.post(self.url_oauth_path_oauth_token, text=self.fixtures[self.FIXTURE_ACCESS_TOKEN], status_code=200)
            m.get(self.url_using_sec_token_path_using_sec_token,
                  text=self.fixtures[self.FIXTURE_SIMPLE_RESPONSE], status_code=200)

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                # (not expired)
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=3, second=0, tzinfo=UTC)

                r = self.api_client.request(self.api_client.GET,
                                            self.path_using_sec_token,
                                            base=self.url_using_sec_token, sec_id_for_special_token='123')

                self.assertEqual('ok', r['status'])

    def test_full_cycle_request_with_retry(self):
        with requests_mock.mock() as m:
            def _callback():
                m.get(self.url_using_sec_token_path_using_sec_token,
                      text=self.fixtures[self.FIXTURE_SIMPLE_RESPONSE], status_code=200)

            # We have to use a special client for test this
            retry_emu_api_client = RetryEmulationApiClient(_callback)

            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)
            m.post(self.url_oauth_path_oauth_token, text=self.fixtures[self.FIXTURE_ACCESS_TOKEN], status_code=200)
            m.get(self.url_using_sec_token_path_using_sec_token, status_code=401)

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                # (not expired)
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=3, second=0, tzinfo=UTC)

                r = retry_emu_api_client.request(self.api_client.GET,
                                                 self.path_using_sec_token,
                                                 base=self.url_using_sec_token, sec_id_for_special_token='123')

                self.assertEqual('ok', r['status'])

    def test_full_cycle_request_with_retry_then_fail(self):
        with requests_mock.mock() as m:
            fixture_public_key = self.fixtures[self.FIXTURE_PUBLIC_KEY]
            m.get(self.url_public_key_path_public_key, text=fixture_public_key, status_code=200)
            m.post(self.url_oauth_path_oauth_token, text=self.fixtures[self.FIXTURE_ACCESS_TOKEN], status_code=200)
            m.get(self.url_using_sec_token_path_using_sec_token, status_code=400)

            # noinspection PyUnresolvedReferences
            with patch.object(MockAccessTokenApiClient, '_get_time_now') as _get_time_now:
                # (not expired)
                _get_time_now.return_value = datetime(year=2018, month=3, day=22, hour=10,
                                                      minute=3, second=0, tzinfo=UTC)

                with self.assertRaises(self.api_client.HttpError):
                    self.api_client.request(self.api_client.GET,
                                            self.path_using_sec_token,
                                            base=self.url_using_sec_token, sec_id_for_special_token='123')
