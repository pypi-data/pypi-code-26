import talib
import pandas as pd
import macrofi.event_selection.performance
from cached_property import cached_property


def signal_to_pos(signal, init_pos=1, level=0.5):
    """
    将信号转换为仓位，默认1表示和基准一样
    :param signal:
    :param init_pos:
    :param level:
    :return:
    """
    pos = init_pos * len(signal)
    pos += pos + signal * level
    return pos.fillna(0)


def zscore(ts, timeperiod=250):
    """对时间序列进行标准化处理"""
    zs = pd.Series((ts.values - talib.MA(ts.values, timeperiod=timeperiod)) /
                   talib.STDDEV(ts.values, timeperiod=timeperiod), index=ts.index)
    return zs.dropna()


def trade_to_curve():
    pass


class StatEngine(object):
    def __init__(self, euqity_fn):
        self._stats = [i for i in dir(macrofi.event_selection.performance) if not i.startswith('_')]


class Backtest(object):
    """针对单因子的的回测，资产一般为基准指数，pos为交易日起点的持仓"""

    def __init__(self, pos, base):
        self._base = base
        self._pos = pos

    @cached_property
    def base_pct(self):
        return self._base.pct_change()

    @cached_property
    def base_ret(self):
        return self._base.diff(periods=1)

    @cached_property
    def ret(self):
        """日绝对涨跌量"""
        return self.curve.diff(periods=1)

    @cached_property
    def pct(self):
        """日涨跌幅"""
        return self.curve.pct_change()

    @cached_property
    def curve(self):
        """
        净盈利曲线

        :return:
        """
        return (self._pos * self.base_pct + 1).cumprod()

    @cached_property
    def norm_curve(self):
        """归一化净值"""
        nc = (1 + self._pos * self.base_pct).cumprod()
        nc[0] = 1
        return nc

    @cached_property
    def norm_ret(self):
        return self.pos * self.base_ret

    @cached_property
    def norm_base(self):
        """归一化基准"""
        return self._base / self._base[0]

    @cached_property
    def pos(self):
        return self._pos

    def trade(self):
        """
        调仓点
        :return:
        """


def case1():
    from datetime import datetime
    from pyfi import WindHelper
    from macrofi.event_selection import mg
    import talib
    import pandas as pd
    begin_date = datetime(2011, 1, 1)
    end_date = datetime(2017, 1, 1)
    shuini = WindHelper.edb(codes="水泥价格指数", begin_date=begin_date, end_date=end_date).iloc[:, 0]
    event_name = "mg"
    event = eval("mg")
    mg = mg(shuini, 1, 47, 2.4)
    print(mg)
    # zscore = pd.Series(((mg - talib.MA(mg, timeperiod=600)) / talib.STDDEV(mg, timeperiod=600)),
    #                    index=shuini.index).dropna()
    mg = mg.shift(2).dropna()
    pos = mg.apply(lambda x: 0 if x > 0 else 1)

    from macrofi.event_selection import Backtest
    base = WindHelper.wsd(code="gz10yind", begin_date=begin_date, end_date=end_date, paras=["close"]).iloc[:, 0]
    bt = Backtest(pos, base)
    from macrofi.event_selection.performance import excess_sp
    print(excess_sp(bt.pct, bt.base_pct))


if __name__ == "__main__":
    case1()
