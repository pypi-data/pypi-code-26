from collections import defaultdict

from ...api_client import BaseApiClient, SecRefreshTokenMixin, SecAccessTokenMixin


class MockLogger(object):
    def __getattr__(self, item):
        def _mock(*args, **kwargs):
            pass

        return _mock


logger = MockLogger()


class MockApiClient(BaseApiClient):
    class HttpError(Exception):
        pass

    class RequestError(Exception):
        pass

    def _raise_performing_request_error(self, *args, **kwargs):
        raise self.RequestError(*args)

    def _raise_http_error(self, *args, **kwargs):
        raise self.HttpError(*args)

    def _get_auth_string(self):
        return 'Bearer foo'

    def _get_logger(self):
        return logger


class MockRefreshTokenApiClient(SecRefreshTokenMixin, MockApiClient):
    def __init__(self,  *args, **kwargs):
        super(MockRefreshTokenApiClient, self).__init__(*args, **kwargs)
        self.mock_store = defaultdict(lambda: defaultdict(dict))

    def _set_cache_sec_refresh_token(self, configuration_id, refresh_token):
        self.mock_store[configuration_id]['refresh_token'] = refresh_token

    def _get_cache_sec_refresh_token(self, configuration_id):
        return self.mock_store[configuration_id]['refresh_token']


class MockAccessTokenApiClient(SecAccessTokenMixin, MockApiClient):
    def __init__(self, *args, **kwargs):
        super(MockAccessTokenApiClient, self).__init__(*args, **kwargs)
        self.mock_store = defaultdict(lambda: defaultdict(dict))

    def _get_cache_public_key(self):
        return self.mock_store['public_key'][0]

    def _set_cache_public_key(self, public_key):
        self.mock_store['public_key'][0] = public_key

    def _set_cache_sec_access_token_expiration(self, configuration_id, expiration):
        self.mock_store[configuration_id]['expiration'] = expiration

    @property
    def _basic_auth_tuple(self):
        return ('foo', 'bar',)

    def _get_cache_sec_access_token_expiration(self, configuration_id):
        return self.mock_store[configuration_id]['expiration']

    def _set_cache_sec_access_token(self, configuration_id, access_token):
        self.mock_store[configuration_id]['access_token'] = access_token

    def get_sec_refresh_token(self, configuration_id):
        return 'REFRESH_TOKEN'

    def _get_cache_sec_access_token(self, configuration_id):
        return self.mock_store[configuration_id]['access_token']
