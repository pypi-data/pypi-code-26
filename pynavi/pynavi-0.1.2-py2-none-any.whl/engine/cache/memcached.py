# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)

from pynavi.engine.cache import BaseCache


class MemcachedCache(BaseCache):

    def __init__(self, client):
        super(MemcachedCache, self).__init__(client)
        self._client = client

    def set(self, k, v, expire=0):
        """将 value(数据值) 存储在指定的 key(键) 中"""
        self._cache.set(k, v, expire)
        pass

    def add(self, k, v, expire=0):
        """将 value(数据值) 存储在指定的 key(键) 中"""
        pass

    def replace(self, k, v, expire=0):
        """替换已存在的 key(键) 的 value(数据值)"""
        pass

    def append(self, k, v):
        """向已存在 key(键) 的 value(数据值) 后面追加数据"""
        pass

    def prepend(self, k, v):
        """向已存在 key(键) 的 value(数据值) 前面追加数据"""
        pass

    def get(self, k):
        """获取存储在 key(键) 中的 value(数据值) ，如果 key 不存在，则返回空"""
        pass

    def mget(self, *ks):
        """获取存储在 key(键) 中的 value(数据值) ，如果 key 不存在，则返回空"""
        pass

    def delete(self, k):
        """删除已存在的 key(键)"""
        pass

    def incr(self, k, increment=1):
        """对已存在的 key(键) 的数字值进行自增操作"""
        pass

    def decr(self, k, decrement=1):
        """对已存在的 key(键) 的数字值进行自减操作"""
        pass
