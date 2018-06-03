# -*- coding: utf-8 -*-
"""
指数相关数据接口
==========================================
"""
import requests
import pandas as pd
import tushare as ts


def index_all():
    """指数行情接口"""
    return ts.get_index()

def get_all_index_sh():
    """获取上海证券交易所所有指数的实时行情"""
    url = "http://www.sse.com.cn/js/common/indexQuotes.js"
    res = requests.get(url).text
    lines = res.split("\n")
    lines = [x.replace('_t.push(', "").strip(");'") for x in lines if "_t.push(" in x]
    lines = [
        eval(line, type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
        for line in lines
    ]

    index_sh = pd.DataFrame(lines)
    index_sh = index_sh[['JC', 'ZSDM', 'abbr', 'ZRSP', 'DRKP', 'DRSP', 'DRZD', 'DRZX', 'ZDF']]
    index_sh = index_sh.rename(columns={
        'JC': 'name',
        'ZSDM': 'code',
        'abbr': 'kind',
        'ZRSP': 'preclose',
        'DRKP': 'open',
        'DRSP': 'close',
        'DRZD': 'high',
        'DRZX': 'low',
        'ZDF': 'change'
    })

    # index_sh.astype()
    return index_sh

