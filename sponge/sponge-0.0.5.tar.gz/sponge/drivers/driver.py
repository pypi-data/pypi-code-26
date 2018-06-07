#!/usr/bin/env python
# encoding: utf-8


"""
@author: william
@contact: 1342247033@qq.com
@site: http://www.xiaolewei.com
@file: driver.py
@time: 22/05/2018 16:12
"""


class Driver(object):

    def get(self, key):
        '''
        :param key:
        :return:
        '''
        raise NotImplemented

    def put(self, key, value, secs=0):
        '''

        :param key:
        :param value:
        :param secs:
        :return:
        '''
        raise NotImplemented

    def increase(self, key, value=1):
        '''

        :param key:
        :param value:
        :return:
        '''
        raise NotImplemented

    def decrease(self, key, value=1):
        '''

        :param key:
        :param value:
        :return:
        '''
        raise NotImplemented

    def forget(self, key):
        '''

        :param key:
        :return:
        '''
        raise NotImplemented

    def forever(self, key, value):
        '''

        :param key:
        :param value:
        :return:
        '''
        raise NotImplemented

    def flush(self):
        '''

        :return:
        '''
        raise NotImplemented
