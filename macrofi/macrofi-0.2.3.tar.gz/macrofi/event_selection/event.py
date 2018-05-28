import talib
import pandas as pd

rule = {
    "z_trans": {"window": [1, 1, 700]},
    "mg": {"short_period"}
}


def mg(data, args):
    """
    3个参数
    data为series类型
    均线缺口
    args[0]:short period
    args[1]:long period
    args[2]: base line
    """
    data = data.ffill()
    ind = data.rolling(window=args[0]).mean() - data.rolling(window=args[1]).mean() - args[2]
    return ind


def cmo(data, args):
    """
    1个参数，趋势指标，返回Series
    """
    arg1 = args[0]
    data = data.ffill()
    ind = pd.Series(talib.CMO(data.values, timeperiod=arg1), index=data.index)
    return ind


def mom(data, args):
    """
    1个参数
    momentum,多日的涨幅
    :param data: pandas.Series
    :param args: args[0]->timeperiod
    :return: pandas.Series
    """
    data = data.ffill()
    ind = pd.Series(talib.MOM(data.values, timeperiod=args[0]), index=data.index)
    return ind


def wmom(data, args):
    """
    1个参数
    加权mom指标，多个不同时间端的涨幅的加权和
    :param data:
    :param args:
    :return:
    """
    ind = (mom(data, args[0])
           + mom(data, args[0])
           + mom(data, args[0])) / 3.0
    return ind


def threshold(data, args):
    """
    1个参数
    阈值指标:阈值.针对一些缺口指标，如主营业务收入累积同比增速和财务费用增速差

    :param data: pandas.Series

    :param args: args[0] threshod，if > threshold, generate a signal

    :return: pandas.Series
    """
    threshold = args[0]
    return data - args[0]


if __name__ == "__main__":
    print()
