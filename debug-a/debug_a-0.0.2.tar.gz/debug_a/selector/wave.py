# -*- coding: utf-8 -*-

"""
根据波动大小选股
=============================================
"""

# TODO(ZB, 0): 最近五个交易日的平均波动在5个点以上
from datetime import datetime
from debug_a.collector.realtime import klines

code = '603655'
code = '600122'

def wave(code):
    data = klines(code)
    data = data.iloc[0:5]
    data['wave_rate'] = (data['high'] - data['low']) / data['open']
    avg_wr = sum(data['wave_rate']) / len(data)
    avg_tor = sum(data['tor']) / len(data)
    return {
        "code": code,
        "5日平均波动": avg_wr,
        "5日平均换手": avg_tor/100
    }

