# -*- coding: utf-8 -*-

"""
历史数据接口
=======================================================================================
"""

import tushare as ts


def hist_market(date):
    """历史行情数据

    :param date: str: 指定日期，如 "2018-03-19"
    :return:
    """
    hm = ts.get_day_all(date)
    hm['date'] = date
    return hm


