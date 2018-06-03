# -*- coding: utf-8 -*-

"""
交易信号处理模块
==================================================================
"""
import os
from debug_a import DATA_DIR
import time


sig_file = os.path.join(DATA_DIR, "signal.txt")



def write_sig(sig):
    """写入交易信号

    :param sig: dict: 交易信号
                {
                "code": 股票代码,
                "name": 股票名称,
                "strategy": 策略名称,
                "reason": 入选原因,
                "trade_type": 交易类型（买入or卖出）,
                "cur_price": 当前价格,
                "time": 时间
                }
    :return:
    """
    with open(sig_file, "a", encoding="utf-8") as f:
        f.write(sig+'\n')

def read_sig_latest(interval=600):
    """读取最新的交易信号

    :return:
    """
    with open(sig_file, "r", encoding="utf-8") as f:
        f.readline()
        sigs = f.readlines()

    sig_latest = [sig for sig in sigs if time.time() - float(sig['time']) < interval]
    return sig_latest

def backup_and_empty_sig_file():
    """备份并清空sig_file"""
    bu_file = os.path.join(DATA_DIR, "signal_backup_%s.txt" % str(int(time.time())))
    with open(sig_file, "r", encoding="utf-8") as f:
        f.readline()
        sigs = f.readlines()

    with open(bu_file, "w", encoding="utf-8") as f:
        f.writelines(sigs)

    with open(sig_file, "w", encoding="utf-8") as f:
        f.write("last_back_up_file: " + bu_file + "\n")

