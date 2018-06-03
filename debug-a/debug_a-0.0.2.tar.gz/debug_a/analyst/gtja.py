# coding: utf-8
"""
国泰君安 - 对账单 - 分析
===============================================================================
"""

import pandas as pd



# path = r"C:\ZB\Life\金融\对账单\国泰君安_对账单_20160329_20180522.csv"
path = r"C:\ZB\tgja_20160329_20180522.csv"

def read_data(path):
    data = pd.read_csv(path)
    data.columns = [x.strip("\t=") for x in data.columns]

    for col in data.columns:
        try:
            data[col] = data[col].apply(lambda x: x.strip("\t="))
        except:
            continue
    return data

data = read_data(path)

def cal_gain(data, cur_cap=0):
    """计算账户整体盈亏
    账户整体盈亏 = 入金 + 当前市值 - 出金
    """
    res = data.groupby(by='交易类型').sum()['发生金额']
    return -res['证券转银行'] - res['银行转证券'] + cur_cap

def cal_share_gain(data):
    """计算所有个股盈亏
    个股盈亏 = 卖出 + 当前市值 - 买入
    """
    data = data[data['证券名称'] != ""]
    res = data.groupby(['证券名称', '交易类型']).sum()['成交金额']
    shares = res.index.levels[0]
    share_gains = []
    for share in shares:
        try:
            print(share, " - 总盈亏：")
            stg = res[share]['证券卖出'] - res[share]['证券买入']
            print(stg, '\n')
            share_gains.append((share, stg))
        except:
            print("\nerro: ", res[share])
    return share_gains

def get_share_detail(share):
    """获取个股的交易记录详情"""
    col_need = ['交收日期', '证券名称', '交易类型', '成交价格', '成交数量', '成交金额']
    detail = data[data['证券名称'] == share][col_need]
    return detail


