# encoding: utf-8
import math
import numpy as np
from macrofi.event_selection.factor_event import *

POSITIVE = 2  # 当event_value超过一定的值的时候，产生做多信号；或者event_value低于一定的值的时候，产生做空信号。
NEGATIVE = -2  # 当event_value超过一定值的时候，产生做空信号
POSITIVE_RELATED = 1  # 正向线性相关信号
NEGATIVE_RELATED = -1  # 反向线性相关信号
UP = 1  # 高位产生信号
DOWN = -1  # 低位产生信号
ALL = 0  # 始终有信号含义

event_dict = {"e001": e001}


def bool_event(event_value, relation, type):
    """翻译为bool类型的多空信号，1做多，0无信号，-1做空"""
    if relation == POSITIVE and type:
        return 1 if event_value > 0 else 0
    elif relation == NEGATIVE:
        return 0 if event_value > 0 else 0


def pos_transfer(event_value):
    """将正向事件值转换为持仓信号"""
    return 1 if event_value > 0 else 0  # 做多信号或者无信号


def neg_tranfer(event_value):
    """将负向事件值转换为持仓信号"""
    return -1 if event_value > 0 else 0  # 做空信号或者无信号


def sharpe_ratio(series, risk_free_rate=0.03):
    """计算夏普比率
    :param series: 
    :param risk_free_rate: 
    :return: 
    """
    daily = series[1:].values / series[:-1] - 1
    sp = math.sqrt(250) * (np.average(daily) - risk_free_rate / 250.0) / np.std(daily)
    return sp


def z_trans(data, window=700):
    """移动平均标准化"""
    return (data - data.rolling(window=window)) / data.rolling(window=window).std()