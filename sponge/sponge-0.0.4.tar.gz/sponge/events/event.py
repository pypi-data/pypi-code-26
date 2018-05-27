#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: event.py
@time: 24/05/2018 23:05
"""


class CacheEvent(object):

    def __init__(self, key):
        self._key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key
