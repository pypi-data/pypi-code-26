# 经济：d(工业增加值)，d(固定资产投资)，d(社融)
# 通胀：CPI + d(PPI)
# 政策&资金：R007绝对水平，R007月度变化
# 海外：d(美债利率), d(美元指数)
# 估值：IP和CPI拟合
from macrofi.data_agent import *
from pyfi import WindHelper


def ip():
    pass


class ZYModel(object):

    def __init__(self):
        self.min_date = None
        self.groups = {
            "eco": ["ip", "fai", "tsf"],
            "inf": ["cpi", "ppi"],
            "mon": ["r007", "delta_r007"],
            "sea": ["usa10y", "usaindex"],
            "val": ["val_spread"]
        }
        self.begin_date = datetime(2006, 1, 1)
        self.end_date = datetime(2018, 1, 1)
        self.ip = WindHelper.edb(codes="ip", begin_date=self.begin_date,
                                 end_date=self.end_date)



    def generator(self, cur_date):
        """
        返回当天的分值以及各分项的值
        """
        pass

    def train(self, begin_date, end_date):
        pass


    def eco(self, begin_date, end_date):
        """返回基本面打分"""
        pass
