from urllib.parse import urlparse
import logging
import requests
from . import auth_utils


LOGGER = logging.getLogger('angou_bitmex')


class _BitmexNonceAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def __call__(self, r):
        nonce = auth_utils.generate_nonce()

        parsed_url = urlparse(r.url)
        path = parsed_url.path
        if parsed_url.query:
            path += '?' + parsed_url.query

        r.headers.update({
            'api-nonce': str(nonce),
            'api-signature': auth_utils.generate_signature(self.api_secret, r.method, path, nonce,
                                                           r.body or ''),
            'api-key': self.api_key,
        })

        return r


class InvalidJSON(Exception):
    pass


class RestError(Exception):
    def __init__(self, code, text, message=None):
        super().__init__(f'HTTP {code}: {message or ""}')
        self.code = code
        self.text = text
        self.message = message


class RestBadRequestError(RestError):
    pass


class RestRateLimitExceededError(RestError):
    def __init__(self, code, text, retry_after):
        super().__init__(code, text)
        self.retry_after = retry_after


class RestTemporaryDownError(RestError):
    pass


class RestSession:
    def __init__(self, domain, api_key, api_secret, timeout=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self._base_url = f'https://{domain}/api/v1'
        self._session = requests.Session()
        self._session.headers.update({
            'user-agent': 'angou-bitmex-yo',
            'content-type': 'application/json',
            'accept': 'application/json',
        })
        self._session.auth = _BitmexNonceAuth(api_key, api_secret)

    def request(self, verb, path, query=None, postdict=None):
        LOGGER.debug('%s %s query=%s postdict=%s', verb, path, query, postdict)
        r = self._session.request(verb, self._base_url + path, json=postdict, params=query,
                                  timeout=self.timeout)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            if r.status_code == 400:
                try:
                    err_obj = r.json()
                    raise RestBadRequestError(r.status_code, r.text, err_obj['error']['message'])
                except (ValueError, KeyError):
                    pass
            elif r.status_code == 429:
                retry_after = None
                try:
                    retry_after = int(r.headers['Retry-After'])
                except (ValueError, KeyError):
                    pass
                raise RestRateLimitExceededError(r.status_code, r.text, retry_after)
            elif r.status_code == 503:
                raise RestTemporaryDownError(r.status_code, r.text)
            raise RestError(r.status_code, r.text)
        else:
            try:
                return r.json()
            except ValueError:
                raise InvalidJSON()
