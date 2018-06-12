# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)


def singleton(cls, *args, **kw):
    """
    单例类装饰器
    :param cls:
    :param args:
    :param kw:
    :return:

    使用方法：

    @singleton
    class Test(object):
        ...

    """
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)

        return instances[cls]

    return _singleton
