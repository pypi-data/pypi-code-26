# coding: utf-8
"""
平安证券 - 对账单 - 分析
===============================================================================
"""
import os
import pandas as pd



# path = r"C:\Users\Mike\Desktop\pazq_records"

def read_data(path):
    files = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".xls")]

    res = pd.DataFrame()

    for file in files:
        data = pd.read_csv(file, encoding='gbk', sep='\t')
        res = res.append(data, ignore_index=True)

    res.columns = [x.strip('"=') for x in res.columns]
    for col in res.columns:
        res[col] = res[col].astype(str)
        res[col] = res[col].apply(lambda x: x.strip('"='))
    res.sort_values("发生日期", ascending=False, inplace=True)
    res.reset_index(drop=True, inplace=True)
    res.drop(['备注', 'Unnamed: 21'], axis=1, inplace=True)
    float_col = ['发生金额', '成交均价', '成交数量', '成交金额', '股份余额',
                 '手续费', '印花税', '资金余额', '委托价格', '委托数量', '过户费']
    for col in float_col:
        res[col] = res[col].astype(float)
    return res


def cal_gain(data):
    """根据交易数据，计算总盈亏"""
    res = dict(data.groupby('业务名称').sum()['发生金额'])
    total_gain = -res['银证转出'] - res['银证转入']
    return round(total_gain, 4)

def cal_share_gain(data):
    """计算个股操作盈亏"""
    data = data[data['证券代码'] != "nan"]
    res = data.groupby(['证券名称', '业务名称']).sum()['成交金额']
    shares = res.index.levels[0]
    share_gains = []
    for share in shares:
        try:
            print(share, " - 总盈亏：")
            stg = res[share]['证券卖出清算'] - res[share]['证券买入清算']
            print(stg, '\n')
            share_gains.append((share, stg))
        except:
            print("\nerro: ", res[share])
    return share_gains



