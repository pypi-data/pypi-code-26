import logging
import requests
from . import auth_utils


LOGGER = logging.getLogger('angou_poloniex')


class _PoloniexAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, r):
        r.headers.update({
            'Sign': auth_utils.generate_signature(self.api_secret, r.body or ''),
            'Key': self.api_key,
        })
        return r


class InvalidJSON(Exception):
    pass


class RestError(Exception):
    pass


class RestSession:
    def __init__(self, api_key, api_secret, timeout=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self._session = requests.Session()
        self._auth = _PoloniexAuth(api_key, api_secret)

    @staticmethod
    def _postprocess(r):
        r.raise_for_status()
        try:
            resp = r.json()
        except ValueError:
            raise InvalidJSON()
        if 'error' in resp:
            raise RestError(str(resp['error']))
        return resp

    def call_public(self, command, params=None):
        LOGGER.debug('GET %s %s', command, params)

        params = params or {}
        params['command'] = command

        return self._postprocess(self._session.request(
            'GET', 'https://poloniex.com/public', params=params, timeout=self.timeout))

    def call_auth(self, command, params=None):
        LOGGER.debug('POST %s %s', command, params)

        params = params or {}
        params.update({
            'command': command,
            'nonce': auth_utils.generate_nonce(),
        })

        return self._postprocess(self._session.request(
            'POST', 'https://poloniex.com/tradingApi', data=params, auth=self._auth,
            timeout=self.timeout))
