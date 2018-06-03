# -*- coding: utf-8 -*-
"""实用工具集
========================================================================
"""

import functools
import os
import time as t
from datetime import datetime
import tushare as ts
import json
from threading import Lock
lock = Lock()

from debug_a import LOG_DIR
# -----------------------------------------------------------------------------

def read_json(file):
    lock.require(3)
    data = json.load(open(file, 'r', encoding='utf-8'))
    lock.release()
    return data

def write_json(file, data):
    lock.require(3)
    json.dump(data, open(file, 'w', encoding='utf-8'), indent=2)
    lock.release()

# -----------------------------------------------------------------------------
trade_calendar = ts.trade_cal()  # tushare提供的交易日历

def is_trade_day(date, trade_calendar=trade_calendar):
    """判断date日期是不是交易日

    :param date: str or datetime.date, 如 2018-03-15
    :param trade_calendar: 交易日历
    :return: Bool
    """

    trade_day = trade_calendar[trade_calendar["isOpen"] == 1]
    trade_day_list = list(trade_day['calendarDate'])
    if isinstance(date, datetime):
        date = str(date.date())
    if date in trade_day_list:
        return True
    else:
        return False


def is_in_trade_time():
    """判断当前是否是交易时间"""
    today = str(datetime.now().date())
    if not is_trade_day(today):  # 如果今天不是交易日，返回False
        return False
    t1 = today + " " + "09:30:00"
    t1 = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S")
    t2 = today + " " + "11:30:00"
    t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
    t3 = today + " " + "13:00:00"
    t3 = datetime.strptime(t3, "%Y-%m-%d %H:%M:%S")
    t4 = today + " " + "15:00:00"
    t4 = datetime.strptime(t4, "%Y-%m-%d %H:%M:%S")
    if t1 <= datetime.now() <= t2 or t3 <= datetime.now() <= t4:
        return True
    else:
        return False


def split_time_into_span(interval):
    """根据interval把交易时间切割成多个间隔"""
    today = datetime.now().date().__str__()
    t1 = int(datetime.strptime(today + ' ' + "09:30:00",
                               "%Y-%m-%d %H:%M:%S").timestamp())
    t3 = int(datetime.strptime(today + ' ' + "13:00:00",
                               "%Y-%m-%d %H:%M:%S").timestamp())
    time_span = []
    keys_len = int(60 * 60 * 2 / interval)

    tt1 = t1
    tt3 = t3
    for i in range(keys_len):
        tt2 = tt1 + interval
        tt4 = tt3 + interval
        span1 = {
            "start_time": tt1,
            "end_time": tt2
        }
        span2 = {
            "start_time": tt3,
            "end_time": tt4
        }
        time_span.append(span1)
        time_span.append(span2)
        tt1 = tt2
        tt3 = tt4
    return time_span


def get_recent_trade_days(date, n=10):
    """返回date(含)之前(或之后)的 n个交易日日期"""
    assert is_trade_day(date), "输入的date必须是交易日"
    tc = ts.trade_cal()
    tct = tc[tc['isOpen'] == 1]
    tct.reset_index(drop=True, inplace=True)
    tcts = list(tct['calendarDate'])
    date_i = tcts.index(date)
    if n > 0:
        rtd = tcts[date_i+1:date_i+n+1]
    else:
        rtd = tcts[date_i+n:date_i+1]
    return rtd
# -----------------------------------------------------------------------------

log_file = os.path.join(LOG_DIR, "debug_a.log")
def create_logger(name='debug_a', log_file=log_file, cmd=True):
    """define a logger for your program

    parameters
    ------------
    log_file     file name of log
    name         name of logger

    example
    ------------
    logger = create_logger('example.log',name='logger',)
    logger.info('This is an example!')
    logger.warning('This is a warn!')

    """
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # set format
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    # file handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # cmd handler
    if cmd:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger


def time_cost(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        start = t.time()
        # 调用被装饰的函数
        print('正在运行函数 %s() ...' % func.__name__)
        res = func(*args, **kw)
        end = t.time()
        print('函数 %s() 运行耗时：%.2f 秒' % (func.__name__, end - start))
        return res
    return wrapper

# TODO: 添加一个装饰器，将某一个函数循环执行，直到条件不满足


# TODO: 创建一个股票监控参数个性化生成的函数


def print_constitutions(explain=False):
    from debug_a import constitution as cs
    cs = cs.__dict__
    del_keys = [i for i in cs.keys() if "__" in i]
    for i in del_keys:
        cs.pop(i)
    for c in cs.items():
        if explain:
            print(c[0]+': ', c[1]['content'])
            print("explain：%s" % c[1]['explain'], '\n')
        else:
            print(c[0]+': ', c[1]['content'], '\n')
