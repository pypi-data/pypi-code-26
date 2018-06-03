# -*- coding: utf-8 -*-
"""
均线选股系统
===========================================
"""
from debug_a.collector.realtime import bars
import tushare as ts
# from datetime import datetime

cons = ts.get_apis()

"""
5日均线上穿10日均线1个点
===========================================
"""

def is_ma5_over_ma10(code):
    bar = ts.bar(code, conn=cons, ma=[5, 10])
    date_sel = str(bar.index[0].date())
    bar_today = dict(bar.iloc[0])
    ma5 = bar_today['ma5']
    ma10 = bar_today['ma10']
    if ma5 > ma10 * 1.01:
        code_res = {
            "code": code,
            "date_sel": date_sel,
            "ma5": ma5,
            "ma10": ma10
        }
        print(code_res)
        return code_res
    else:
        return False


def ma5_over_ma10():
    """选取今日市场中所有 ma5 > 1.01*ma10 的股票"""
    data = ts.get_today_all()
    res = []
    for i in data.index:
        d = data.iloc[i]
        code = d['code']
        name = d['name']
        try:
            if code_res:
                code_res = is_ma5_over_ma10(code)
                code_res['name'] = name
                res.append(code_res)
            else:
                continue
        except:
            continue
    return res


"""
偏离5日均线5个点以上
===========================================
"""

def is_deviate_ma5(code):
    bar = ts.bar(code, conn=cons, ma=[5])
    cur_price, ma5 = bar.iloc[0][['close', 'ma5']]
    if cur_price < ma5*0.95:
        return {
            "code": code,
            "ma5": ma5,
            "price": cur_price
        }
    else:
        return False


def deviate_ma5():
    raise NotImplementedError



