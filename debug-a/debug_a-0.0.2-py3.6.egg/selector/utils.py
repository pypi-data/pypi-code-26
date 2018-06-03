# coding: utf-8

from debug_a.collector.realtime import klines


def cal_stairway_prices(code, klines_d=None):
    """阶梯价格区间计算"""

    # 阶梯价格区间定义
    # 1、日k线 - MA5/MA10/MA20
    # 2、周k线 - MA5/MA10/MA20
    # 3、月k线 - MA5/MA10/MA20
    # 4、近20个交易日的最高价和最低价（以收盘价为准）
    # 5、近40个交易日的最高价和最低价（以收盘价为准）
    # 6、近60个交易日的最高价和最低价（以收盘价为准）

    if klines_d is None:
        klines_d = klines(code=code)
    klines_d = klines_d.sort_values('date', ascending=False)
    klines_d.reset_index(drop=True, inplace=True)
    close_seq = klines_d['close']



