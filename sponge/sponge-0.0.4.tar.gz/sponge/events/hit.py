#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: hit.py
@time: 24/05/2018 23:12
"""
from .event import CacheEvent


class CacheHit(CacheEvent):

    def __init__(self, key, value):
        CacheEvent.__init__(key)
        self._value = value

    @property
    def value(self):
        return self._value
