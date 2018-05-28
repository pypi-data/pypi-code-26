import abc
from datetime import datetime

import six
from pytz import UTC

from .public_key_mixin import PublicKeyMixin
from . import resources
from .. import jwt_util


@six.add_metaclass(abc.ABCMeta)
class SecAccessTokenMixin(PublicKeyMixin):
    @abc.abstractmethod
    def _get_cache_sec_access_token(self, configuration_id):
        """
        Return sec access token from cache

        """

    @abc.abstractmethod
    def _set_cache_sec_access_token(self, configuration_id, access_token):
        """
        Set sec refresh token to cache

        """

    @abc.abstractmethod
    def _get_cache_sec_access_token_expiration(self, configuration_id):
        """
        Return sec access token expiration time (as Python datetime object)

        """

    @abc.abstractmethod
    def _set_cache_sec_access_token_expiration(self, configuration_id, expiration):
        """
        Return sec access token expiration time (as Python datetime object)

        """

    @property
    @abc.abstractmethod
    def _basic_auth_tuple(self):
        """
        Return basic auth tuple with name and password

        """

    @abc.abstractmethod
    def get_sec_refresh_token(self, configuration_id):
        """
        Return refresh token

        """

    def _reset_cache_public_key(self):
        # TODO: make method abstract for required overriding
        pass

    def get_sec_access_token(self, configuration_id):
        if not self._is_sec_access_token_expired(configuration_id):
            # Get cached access token from store
            return self._get_cache_sec_access_token(configuration_id)

        refresh_token = self.get_sec_refresh_token(configuration_id)

        data = 'grant_type=refresh_token&client_id=script&refresh_token={}'.format(refresh_token)

        json = self.request(self.POST, 'token',
                            base=resources.OAUTH_SERVICE_ENDPOINT,
                            data=data,
                            extra_headers={
                                'Content-Type': 'application/x-www-form-urlencoded',
                                'Accept': 'application/json'
                            },
                            basic_auth_tuple=self._basic_auth_tuple)

        access_token = json['access_token']
        expiration_datetime = self.parse_access_token_expiration(access_token)
        self._set_cache_sec_access_token(configuration_id, access_token)
        self._set_cache_sec_access_token_expiration(configuration_id, expiration_datetime)

        return access_token

    def _is_sec_access_token_expired(self, configuration_id):
        sec_access_token_expiration = self._get_cache_sec_access_token_expiration(configuration_id)

        if not sec_access_token_expiration:
            return True

        now = self._get_time_now()
        seconds_diff = (sec_access_token_expiration - now).total_seconds()

        if seconds_diff <= 20:
            return True

        return False

    def _get_time_now(self):
        return datetime.now(UTC)

    def parse_access_token_expiration(self, access_token):
        public_key = self.get_public_key()
        util = jwt_util.JWTUtil(access_token)
        exp_string = util.extract_expiration_string(public_key)
        expiration_datetime = datetime.utcfromtimestamp(exp_string).replace(tzinfo=UTC)
        return expiration_datetime
