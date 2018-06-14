# -*- coding: utf-8 -*-
"""
    zebe.util.datetime_util
    ~~~~~~~~~~~~~~~~

    日期和时间工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import calendar
import datetime
import time


def get_total_day_of_year(year):
    """
    获取某一年的总天数
    :param year: 年份
    :return: 返回总天数，例如364、365、366
    """
    total_day = 0
    for i in range(12):
        month_range = calendar.monthrange(year, i + 1)
        total_day += month_range[1]
    return total_day


def get_which_day_of_year(year, month, day):
    """
    获取某一天在那一年中是第几天
    :param year: 年
    :param month: 月
    :param day: 日
    :return: 返回第几天，例如元旦节是第1天
    """
    target_day = datetime.date(year, month, day)
    day_count = target_day - datetime.date(target_day.year - 1, 12, 31)  # 减去上一年最后一天
    return day_count.days


def get_start_of_day(which_day):
    """
    获取某一天的开始时间
    :param which_day: 日期
    :return: 返回某一天的开始时间，datetime格式
    """
    return datetime.datetime.strptime(get_start_of_day_str(which_day), "%Y-%m-%d %H:%M:%S")


def get_end_of_day(which_day):
    """
    获取某一天的结束时间
    :param which_day: 日期
    :return: 返回某一天的结束时间，datetime格式
    """
    return datetime.datetime.strptime(get_end_of_day_str(which_day), "%Y-%m-%d %H:%M:%S")


def get_start_of_day_str(which_day):
    """
    获取某一天的开始时间
    :param which_day: 日期
    :return: 返回某一天的开始时间，字符串格式，例如：2018-01-01 00:00:00
    """
    return which_day.strftime("%Y-%m-%d") + ' 00:00:00'


def get_end_of_day_str(which_day):
    """
    获取某一天的结束时间
    :param which_day: 日期
    :return: 返回某一天的结束时间，字符串格式，例如：2018-01-01 23:59:59
    """
    return which_day.strftime("%Y-%m-%d") + ' 23:59:59'


def get_today_str():
    """
    获取今天的日期字符串
    :return: 例如：2018-01-01
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def get_tomorrow_str():
    """
    获取明天的日期字符串
    :return: 例如：2018-01-02
    """
    return (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


def get_yesterday_str():
    """
    获取昨天的日期字符串
    :return: 例如：2017-12-31
    """
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
