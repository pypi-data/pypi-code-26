# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)

"""策略模式"""


class Strategy(object):
    """策略定义"""

    def action(self, *args, **kwargs):
        raise NotImplementedError


class StrategyContext(object):
    """决策类上下文"""

    def __init__(self, strategy):
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy

    def action(self, *args, **kwargs):
        return self._strategy.action(*args, **kwargs)
