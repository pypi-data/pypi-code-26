# -*- coding: utf-8 -*-

"""
虚拟账户 - 用于仿真交易
============================================================================
"""
import os
from datetime import datetime
import json

from debug_a import ACCOUNT_DIR
from debug_a.collector.realtime import get_price
from debug_a.tools import file_op

class Account:
    def __init__(self, name, fund=-1):
        self.name = name
        self.path = os.path.join(ACCOUNT_DIR, "%s_trade.json" % self.name)
        self.info = {
            "name": self.name,
            "path": self.path,
            "fund": fund,     # 把fund设置为-1表示不限制资金大小
            "trades": {},
            "create_date": datetime.now().date().__str__(),
        }

    def _read_info(self):
        if os.path.exists(self.path):
            self.info = json.load(open(self.path, 'r'))

    def _save_info(self):
        json.dump(self.info, open(self.path, 'w'))

    def buy(self, code, amount, price=None):
        if not price:
            price = get_price(code)
        record = {
            "code": code,
            "amount": amount,
            "price": price,
            "date": datetime.now().date().__str__(),
            "kind": "BUY"
        }
        if code not in self.info['trades'].keys():
            self.info['trades'][code] = []
        self.info['trades'][code].append(record)
        self._save_info()

    def sell(self):
        pass





