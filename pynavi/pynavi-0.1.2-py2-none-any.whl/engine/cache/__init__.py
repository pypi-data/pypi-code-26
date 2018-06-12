# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
import hashlib


class BaseCache(object):
    """缓存基类"""

    def __init__(self, client):
        self._client = client

    def __getattr__(self, name):
        """缓存方法代理"""
        if hasattr(self, name):
            return getattr(self, name)

        return getattr(self._client, name, None)

    @classmethod
    def build_key(cls, prefix='', *args, **kwargs):
        """生成缓存key"""
        key = prefix + '\t'
        key += '\t'.join(args) if args else ''

        if kwargs:
            for k, v in kwargs.items():
                key += '\t{}:{}'.format(str(k), str(v))

        key = key.strip('\t')

        return '{}-{}'.format(prefix, hashlib.md5(key).hexdigest().upper())
