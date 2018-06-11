# -*- encoding: utf-8 -*-
import time
import requests
import logging

from functools import wraps


logger = logging.getLogger(__name__)


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        logger.debug('%s function took %0.3f ms' % (f.__name__, (time2-time1)*1000.0))
        return ret
    return wrap


class Client(object):
    SF_URL = "https://smartflag.herokuapp.com"

    def __init__(self):
        self._env_key = None
        self.session = requests.session()
        self._test_url = None

    def setup(self, environment_key):
        self._env_key = environment_key

    def _get_url(self):
        return self._test_url if self._test_url else self.SF_URL

    def set_test_url(self, url):
        self._test_url = url

    @timing
    def check_flag(self, flag_name, on_failure=False):
        url = "{}/api/v1/{}/{}".format(self._get_url(), self._env_key, flag_name)
        try:
            res = self.session.get(url)
            if res.ok:
                return res.json()['status']
        except Exception as exc:
            logger.error("Something went bad with SmartFlag -> {}: {}".format(exc.__class__.__name__, str(exc)))
            return on_failure

_client = Client()


def setup(environment_key):
    _client.setup(environment_key)


def enabled(flag_name):
    def wrap(func):
        @wraps(func)
        def _wrap(*args, **kwargs):
            if _client.check_flag(flag_name):
                return func(*args, **kwargs)
        return _wrap
    return wrap


def disabled(flag_name):
    def wrap(func):
        @wraps(func)
        def _wrap(*args, **kwargs):
            if not _client.check_flag(flag_name):
                return func(*args, **kwargs)
        return _wrap
    return wrap




