# encoding: utf-8
import pandas as pd
from pyfi import WindHelper

"""
水泥价格指数
冷轧钢板综合价格指数
利率债10年-1年利差指数
"""

def get_shuini():
    """水泥价格"""
    pass


def get_boli(begin_date, end_date):
    """玻璃价格"""
    df = WindHelper.edb(codes=["玻璃综合指数"], begin_date=begin_date, end_date=end_date)
    return df


def get_lzgb(begin_date, end_date):
    """冷轧钢板"""
    mapper = {
        "北京": "S0033141",
        "上海": "S0033136",
        "广州": "S0033131",
        "重庆": "S0033140",
        "成都": "S5706124",
        "西安": "S5706126",
        "杭州": "S5706122"
    }
    df = WindHelper.edb(codes=list(mapper.values()),
                        begin_date=begin_date,
                        end_date=end_date)
    return pd.DataFrame({"lzgb": df.mean(axis=1)})


def get_crb(begin_date, end_date):
    """
    获取CRB的日度数据
    :param begin_date: 
    :param end_date: 
    :return: 
    """
    df = WindHelper.edb(codes=["crb"], begin_date=begin_date, end_date=end_date)
    return df


def get_hs300(begin_date, end_date):
    """
    沪深300
    :return: 
    """
    df = WindHelper.wsd(code="000300.SH", paras=["close"], begin_date=begin_date, end_date=end_date)
    return df


def get_vix(begin_date, end_date):
    """
    
    :param begin_date: 
    :param end_date: 
    :return: 
    """
    df = WindHelper.wsd(code="VIX.GI", begin_date=begin_date, end_date=end_date)
    return df


def get_szzz():
    """
    上证综指
    :return: 
    """
    pass


def get_nhspzs(begin_date, end_date):
    """
    南华商品指数
    :return: 
    """
    df = WindHelper.wsd(code="NH0100.NHF", begin_date=begin_date, end_date=end_date)
    return df


def case1():
    df = get_lzgb(begin_date="2018-01-01", end_date="2018-03-22")
    print(df)


if __name__ == "__main__":
    case1()
