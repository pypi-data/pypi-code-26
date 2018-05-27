#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: forgotten.py
@time: 24/05/2018 23:15
"""
from .event import CacheEvent


class CacheForgotten(CacheEvent):

    def __init__(self, key):
        CacheEvent.__init__(key)
