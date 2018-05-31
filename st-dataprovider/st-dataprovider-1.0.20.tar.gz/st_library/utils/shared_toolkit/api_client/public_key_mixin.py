import abc

import six

from . import resources


@six.add_metaclass(abc.ABCMeta)
class PublicKeyMixin(object):
    @abc.abstractmethod
    def _get_cache_public_key(self):
        """
        Return public key from cache

        """

    @abc.abstractmethod
    def _set_cache_public_key(self, public_key):
        """
        Set public key to cache

        """

    @abc.abstractmethod
    def _reset_cache_public_key(self):
        """
        Reset public key to cache

        """

    def get_public_key(self):
        public_key = self._get_cache_public_key()
        if public_key:
            return public_key

        public_key_bytes = self.request(self.GET, 'token_publickey', base=resources.JWTKEY_ENDPOINT,
                                        extra_headers={'Authorization': None}, raw_content=True)
        public_key = public_key_bytes.decode('utf-8')
        self._set_cache_public_key(public_key)

        return public_key
