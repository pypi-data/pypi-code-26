# -*- coding: utf-8 -*-
"""
计算单只股票的总市值排名和流通市值排名

按市值从小到大进行排名
==========================================
"""
import tushare as ts


class CapSelector:
    def __init__(self):
        self.data = ts.get_today_all()
        self.total_cap_orders = None
        self.circle_cap_orders = None

    def total_cap_order(self):
        """按总市值从小到大排序"""
        data = self.data
        data = data.sort_values(by=["mktcap"])
        data.reset_index(drop=True, inplace=True)
        self.total_cap_orders = data[['code', 'name', 'mktcap']]
        return data[['code', 'name', 'mktcap']]

    def circle_cap_order(self):
        """按流通市值从小到大排序"""
        data = self.data
        data = data.sort_values(by=["nmc"])
        data.reset_index(drop=True, inplace=True)
        self.circle_cap_orders = data[['code', 'name', 'nmc']]
        return data[['code', 'name', 'nmc']]





