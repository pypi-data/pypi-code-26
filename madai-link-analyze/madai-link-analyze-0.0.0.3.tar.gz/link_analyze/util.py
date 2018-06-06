#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/25 20:52
# @Author  : jialun.wjl
# @File    : util.py
# @Software: PyCharm
import time

class Util(object):

    @staticmethod
    def time_now():
        time_array = time.localtime(time.time())
        format_time = time.strftime("%Y%m%d%H%M%S", time_array)
        return format_time
