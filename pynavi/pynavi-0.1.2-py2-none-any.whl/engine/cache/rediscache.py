# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
from redis import StrictRedis

from pynavi.engine.cache import BaseCache


class RedisCache(BaseCache):

    def __init__(self, params):
        self._client = StrictRedis(
            host=params['HOST'],
            port=params['PORT'],
            db=params['DB'],
            password=params['PASSWORD'],
            max_connections=params.get('MAX_CONNECTIONS', 100),
            socket_timeout=params.get('SOCKET_TIMEOUT', 1)
        )
        super(RedisCache, self).__init__(self._client)
