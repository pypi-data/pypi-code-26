# -*- coding: utf-8 -*-

"""
基于成交历史的选股方法
======================================================================
"""
import traceback
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pandas as pd

from debug_a.collector.realtime import ticks, today_market
from debug_a import DATA_DIR


def get_bs_diff(code, date=datetime.now().date().__str__(), threshold=200000, source='spider'):
    """计算大于threshold的买卖单分布"""
    trades = ticks(code, date=date, source=source)
    # TODO: 计算大单成交占总成交的比例
    trades['amount'] = trades['price'] * trades['vol'] * 100
    trades = trades[trades['amount'] > threshold]
    res = dict(trades.groupby('type').sum()['amount'])
    if 2 in res.keys():
        del res[2]
    try:
        assert 0 in res.keys() and 1 in res.keys()
        # assert 0 in res.keys() and 1 in res.keys(), print(res)

        bs_diff = res[0] - res[1]  # 0表示买盘；1表示卖盘
        bs_m = res[0]/res[1]
        return {
            "code": code,
            "买减卖": int(bs_diff),
            "买除卖": round(bs_m, 2),
            "threshold": threshold,
            "date": date
        }
    except:
        # traceback.print_exc()
        return {
            "code": code,
            "买减卖": 0,
            "买除卖": 0,
            "threshold": threshold,
            "date": date
        }

def get_bs_diff_all(codes=None, threshold=200000):
    """获取codes中全部股票的大于threshold的买卖单分布"""
    if codes is None:
        codes = list(today_market(filters=['st', 'tp'])['code'])
    file = os.path.join(DATA_DIR, str(datetime.now().date()) + "_BS选股结果_RAW.txt")

    def _bs_diff(code):
        try:
            res = get_bs_diff(code, threshold=threshold)
            if res['买除卖'] > 2 and res['买减卖'] > 5000000:
                with open(file, 'a', encoding="utf-8") as f:
                    f.write(str(res)+"\n")
            print(res)
        except:
            print('fail:', code)
            traceback.print_exc()

    tpe = ThreadPoolExecutor(100)
    tpe.map(_bs_diff, codes)

def get_bs_top50():
    """获取基于50万以上买卖盘分布的选股结果"""
    TODAY = datetime.now().date().__str__()
    file = os.path.join(DATA_DIR, TODAY + "_BS选股结果_RAW.txt")
    with open(file, "r", encoding="utf-8") as f:
        results = f.readlines()
    results = [eval(x) for x in results]
    df = pd.DataFrame(results)
    df.sort_values('买除卖', inplace=True, ascending=False)
    # df.sort_values('买减卖', inplace=True, ascending=False)
    df_sel = df.head(50)
    csv_file = os.path.join(DATA_DIR, TODAY + "_BS选股结果.csv")
    df_sel.to_csv(csv_file, index=False)
    return df_sel


# TODO: 分析同一个股票的最近N个交易日的买卖盘分布


