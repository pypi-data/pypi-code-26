# -*- coding: utf-8 -*-
"""
监控单只股票
=============================================================
"""
from datetime import datetime
from time import sleep
import pandas as pd
from sklearn.preprocessing import minmax_scale
import matplotlib.pyplot as plt
from debug_a.utils import is_in_trade_time, create_logger, split_time_into_span
from debug_a.xueqiu.utils import open_xueqiu
from debug_a.collector.realtime import bars, ticks, klines
from debug_a import labels

logger = create_logger(name="sm")

"""
============================================================
开发架构：每一个监控函数独立开发
============================================================
"""

# ----------------价格区间监控---------------------------------------

def _price_m(code, low, high):
    bar = bars(code)
    price = float(bar.iloc[0]['price'])

    logger.info("code: %s; cur_price: %s; High: %s; low: %s" % (code, price, high, low))

    if price < low:
        return 1

    if price > high:
        return 0
    return 2


def price_section_monitor(code, low, high, max_nums=3):
    """给定股票的价格区间，当股价偏离区间时，发送预警通知

    一个应用场景是：low对应买入做T机会，high对应卖出A做T机会，以此作为监控目标

    :param code: str: 股票代码
    :param high: float: 区间最高价
    :param low: float: 区间最低价
    :param max_nums: 计数阈值
    :return:

    example
    >>> from debug_a.monitor.single_monitor import price_section_monitor
    >>> code = '600122'; low = 9.20; high = 9.5
    >>> price_section_monitor(code, low, high)
    """
    msg = "执行股票价格区间监控，参数：code(%s), low(%s), high(%s), max_nums(%s)" % (
        code, str(low), str(high), str(max_nums)
    )
    logger.info("start -- " + msg)
    nums = {"over_high": 0, "over_low": 0}
    while True:
        try:
            if nums["over_high"] > max_nums or nums["over_low"] > max_nums:
                open_xueqiu(code)
                break
            if is_in_trade_time():
                res = _price_m(code=code, low=low, high=high)
                if res == 1:
                    nums["over_high"] += 1
                elif res == 0:
                    nums["over_low"] += 1
                sleep(3)
            else:
                logger.info("当前不是交易时间")
                break
        except KeyboardInterrupt:
            break
    logger.info("end -- " + msg)


# ----------------价量关系（待完善）----------------------------------

def pv_relationship(code, interval=300, plot=False):
    """价量关系监控

    :param interval: int: 时间间隔，以秒为单位
    :param code: str: 股票代码，如 "603655"
    :param plot: bool: 默认为False
    :return:
    """
    data = ticks(code=code)
    data['timestamp'] = data["datetime"].apply(lambda x:
                                           int(datetime.strptime(x,
                                        "%Y-%m-%d %H:%M").timestamp()))
    data['amount'] = data['price'] * data['vol']
    time_span = split_time_into_span(interval)
    pvs = []
    for span in time_span:
        start_time = span['start_time']
        end_time = span['end_time']
        data["sel"] = data["timestamp"].apply(lambda x: start_time <= int(x) < end_time)
        data_sel = data[data["sel"] == True]
        data_sel = data_sel.sort_values(by='timestamp')

        # 计算价格变化
        start_price = data_sel.iloc[0]['price']
        end_price = data_sel.iloc[-1]['price']
        price_change = (start_price - end_price) / start_price

        # 计算成交量
        total_vol = sum(data_sel['amount'])
        # detail_vol = dict(data_sel.groupby('type').sum()['amount'])

        # 收集计算结果
        pv = {
            "start_time": start_time,
            "end_time": end_time,
            "price_change": price_change,
            "total_vol": total_vol,
            # "detail_vol": detail_vol,

        }
        pvs.append(pv)
    pvs_df = pd.DataFrame(pvs)
    pvs_df = pvs_df.sort_values('start_time')
    pvs_df = pvs_df.reset_index(drop=True)
    pvs_df["start_time"] = pvs_df["start_time"].apply(lambda x: datetime.fromtimestamp(x))
    pvs_df["end_time"] = pvs_df["end_time"].apply(lambda x: datetime.fromtimestamp(x))
    # 归一化、作图，作图不完善
    if plot:
        y1 = minmax_scale(pvs_df['price_change'])
        y2 = minmax_scale(pvs_df['total_vol'])
        x = pvs_df['start_time']
        plt.figure()
        plt.plot(x, y1, "r-", x, y2, 'b*')
        plt.legend()
    return pvs_df

# ----------------固定间隔通知--------------------------------------

def _single_notify(code):
    """
    构造单只股票的实时动态信息

    :param code: str 股票代码
    :return message: str 信息
    """

    if not isinstance(code, str):
        raise TypeError('code 必须是 str 类型')
    else:
        assert len(code) == 6, "A股代码长度应该为6, " \
                               "当前code(值：%s)长度为%i" % (code, len(code))

    rt = bars(code)

    # 基础信息
    name = rt['name'][0]
    price = round(float(str(rt['price'][0])), 2)
    wave = round(float(rt['high'][0]) - float(rt['low'][0]), 2)

    # 成交量
    vol = str(round(float(rt['amount'][0]) / 10000, 2))

    # 信息模板
    message = """【{0}】当前价【{1}】元，今日累计波动【{2}】元，成交量【{3}】万元。""" \
        .format(name, price, wave, vol)

    return message

def fix_info(code):
    # 定时提醒单只股票的股价变动
    assert is_in_trade_time(), "当前不是交易时间"
    print(datetime.now(), '|', _single_notify(code))


# ----------------挂单监控--------------------------------------

def order_book_monitor(codes, bgd=3000):
    """挂单监控

    :param codes: list or str, 股票代码列表
    :param bgd: int, 大单阈值，默认值为3000,即超过3000手的挂单被认为是大单
    :return:
    """
    logger.info("order_book_monitor(%s) 开始执行 ... " % str(codes))
    loop = True
    while loop:
        assert is_in_trade_time(), "当前不是交易时间"
        bar = bars(codes)
        for i in bar.index:
            try:
                code = bar.loc[i]['code']
                name = bar.loc[i]['name']
                ob_buy = list(bar.loc[i][['b1_v', 'b2_v', 'b3_v', 'b4_v', 'b5_v']])
                ob_buy = [int(x) for x in ob_buy]
                max_buy = max(ob_buy)
                ob_sell = list(bar.loc[i][['a1_v', 'a2_v', 'a3_v', 'a4_v', 'a5_v']])
                ob_sell = [int(x) for x in ob_sell]
                max_sell = max(ob_sell)
                # msg = """{0}({1}): 买单总量 {2}手，卖单总量 {3}手""".format(
                #     code, name, str(sum(ob_buy)), str(sum(ob_sell))
                # )
                # logger.info(msg)

                # 大买单监控
                if max_buy > bgd:
                    msg_b = """{0}({1}): {2}，挂单数量 {3}手""".format(
                        code, name, labels.GDBD['name'], str(max_buy))
                    logger.info(msg_b)

                # 大卖单监控
                if max_sell > bgd:
                    msg_s = """{0}({1}): {2}，挂单数量 {3}手""".format(
                        code, name, labels.GDSD['name'], str(max_sell))
                    logger.info(msg_s)
            except:
                continue
        sleep(10)
    logger.info("order_book_monitor(%s) 执行结束！" % str(codes))


# ----------------均线突破监控--------------------------------------

def average_line_monitor(code, action=None, freq='D', fast=5, slow=10):
    """
    average_line_monitor(code, action='buy', freq='D', fast=5, slow=10)
    :param code: 股票代码
    :param action: 交易方向，可选值 ['buy', 'sell']
    :param freq: k周期，可选值与debug_a.realtime.klines函数中的freq参数一致
    :param fast:
    :param slow:
    :return:
    """
    loop = True
    sig_nums = {
        'buy': 0,
        'sell': 0
    }
    while loop:
        sleep(3)
        data = klines(code, freq=freq)
        last_kl = data.tail(1)
        ma_fast = round(data['close'].tail(fast).mean(), 4)
        ma_slow = round(data['close'].tail(slow).mean(), 4)
        logger.info('%s, ma_fast: %s, ma_slow: %s, action: %s, freq: %s' % (
            code, str(ma_fast), str(ma_slow), action, str((freq, fast, slow))
        ))
        if action == 'buy':
            if ma_fast > ma_slow * 1.002 and last_kl['close'] > last_kl['open']:
                sig_nums['buy'] += 1
                logger.info('meet buy condition, current sig_nums: %i' % sig_nums['buy'])
                if sig_nums['buy'] > 10:
                    print('push sms')
                    open_xueqiu(code)
                    loop = False
            else:
                continue
        elif action == 'sell':
            if ma_fast < ma_slow * 0.998:
                sig_nums['sell'] += 1
                logger.info('meet sell condition, current sig_nums: %i' % sig_nums['sell'])
                if sig_nums['sell'] > 10:
                    print('push sms')
                    open_xueqiu(code)
                    loop = False
            else:
                continue
        else:
            raise ValueError("param action must be 'buy' or 'sell' !")






if __name__ == '__main__':
    code = "603655"
    codes = ['600122', '603655']
    order_book_monitor(codes)

