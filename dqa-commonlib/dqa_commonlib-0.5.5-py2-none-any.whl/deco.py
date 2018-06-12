# -*- coding:utf-8 -*-
# Author: xiaoyaoyuyi
# Mail: 389105015@qq.com

import functools


def record(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print "before called [%s]." % func.__name__
        fn = func(*args, **kwargs)
        print "after called [%s]." % func.__name__
        return fn

    return wrapper
