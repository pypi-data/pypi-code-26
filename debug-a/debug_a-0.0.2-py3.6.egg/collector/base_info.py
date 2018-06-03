# -*- coding: utf-8 -*-

"""
基础数据接口
===================================
"""

import tushare as ts


def market_basic():
    return ts.get_stock_basics()



