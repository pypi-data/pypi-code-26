# encoding: utf-8
# 编写因子事件
import pandas as pd
"""
元事件列表
"""


def e000(factor_series, cur_date, config):
    """
    
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """
    pass


def e001(adjust_factor_series, cur_date, config):
    """
    均值缺口事件函数，只是提供事件函数，不判断方向，不判断未来函数，保持最小功能
    :param adjust_factor_series: series 因子的时间序列
    :param cur_date: (datetime,timestamp or string),cur_date不是买入日期，而是承受波动日期
    :param his_count: int 历史时间窗口大小
    :return: float 返回因子事件值,返回值应该标准化，正值表示应该做多，负值表示应该做空
    """
    # 拆解config字典
    his_count = config["his_count"]
    std_count = config["std_count"]
    # 找到当前日期或者与当前日期最相近的前一个日期
    his_end_num = len(adjust_factor_series[adjust_factor_series.index <= cur_date]) - 1
    # 开始计算信号值的大小
    his_start_num = his_end_num - his_count + 1
    if his_start_num < 0:
        return None
    avg = adjust_factor_series.iloc[his_start_num:his_end_num].mean()  # 不包含his_end_num
    std = adjust_factor_series.iloc[his_start_num:his_end_num].std()
    # 返回信号值
    event_value = adjust_factor_series.iloc[his_end_num] - avg - std_count * std
    return event_value


def digit_decorator(event, relation, type):
    """数字事件封装的装饰器
    :param event: 
    :param relation: 
    :param type_: UP 正值产生信号，DOWN 负值产生信号，ALL正负值都产生信号
    """

    def wrapper(factor_series, cur_date, condig):
        pass


def e002x1(factor_series, cur_date, config):
    """
    连续N个周期上涨幅度超过H.
    默认type=UP
    :return: 
    """
    his_count = config["his_count"]
    threshold = config["threshold"]
    his_end_ind = len(factor_series[factor_series.index <= cur_date]) - 1
    his_start_ind = his_end_ind - his_count
    if his_start_ind >= 0:
        his_wind_series = factor_series.iloc[his_start_ind:his_end_ind + 1]
        count = ((his_wind_series.pct()) > threshold).sum()
        if count == his_count:
            return 1
        else:
            return 0

    else:
        return None


def e002x2(factor_series, cur_date, config):
    """
    连续N个周期下跌幅度都小于H.
    默认type=DOWN
    :return: 
    """
    his_count = config["his_count"]
    threshold = config["threshold"]
    his_end_ind = len(factor_series[factor_series.index <= cur_date]) - 1
    his_start_ind = his_end_ind - his_count - 1  # 收益率需要多算一个
    if his_start_ind >= 0:
        his_wind_series = factor_series.iloc[his_start_ind:his_end_ind + 1]
        count = ((his_wind_series.pct()) < threshold).sum()
        if count == his_count:
            return -1
        else:
            return 0
    else:
        return None


def e002(factor_series, cur_date, config):
    """
    e002x1和e002x2叠加事件
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """
    if e002x1(factor_series, cur_date, config) > 0:
        return 1
    elif e002x2(factor_series, cur_date, config) > 0:
        return -1
    else:
        return 0


def e003x1(factor_series, cur_date, config):
    """
    反转信号，连续N个周期上涨后出现下跌
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """
    his_count = config["his_count"]
    threshold = config["threshold"]
    threshold2 = config["threshold2"]  # 反转幅度
    his_end_ind = len(factor_series[factor_series.index <= cur_date]) - 1
    his_start_ind = his_end_ind - his_count - 1  # 收益率需要多算一个
    if his_start_ind >= 0:
        his_wind_series = factor_series.iloc[his_start_ind:his_end_ind + 1]
        his_wind_returns = his_wind_series.pct()
        his_wind_returns.dropna(inplace=True)
        count = (his_wind_returns[0:-1] > threshold).sum()
        if count == his_count and his_wind_returns[-1] < threshold2:
            return -1
        else:
            return 0
    else:
        return None


def e003x2(factor_series, cur_date, config):
    """
    反转信号，连涨N个周期后下跌后出现上涨
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """
    his_count = config["his_count"]
    threshold = config["threshold"]  # 下跌幅度
    threshold2 = config["threshold2"]  # 反转幅度
    his_end_ind = len(factor_series[factor_series.index <= cur_date]) - 1
    his_start_ind = his_end_ind - his_count
    if his_start_ind >= 0:
        his_wind_series = factor_series.iloc[his_start_ind:his_end_ind + 1]
        his_wind_returns = his_wind_series.pct()
        his_wind_returns.dropna(inplace=True)
        count = (his_wind_returns[0:-1] < threshold).sum()
        if count == his_count and his_wind_returns[-1] > threshold2:
            return 1
        else:
            return 0
    else:
        return None


def e003(factor_series, cur_date, config):
    """
    
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """
    if e003x1(factor_series, cur_date, config) < 0:
        return -1
    elif e003x2(factor_series, cur_date, config) > 0:
        return 1
    else:
        return 0


def e004(factor_series, cur_date, config):
    """
    因子过去N个周期的总涨幅 - 阈值
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """
    his_count = config["his_count"]
    threshold = config["threshold"]
    his_end_num = len(factor_series[factor_series.index <= cur_date]) - 1
    his_start_num = his_end_num - his_count + 1
    ret = factor_series.iloc[his_end_num] / factor_series.iloc[his_start_num] - 1
    event_value = ret - threshold
    return event_value


def e005(factor_series, cur_date, config):
    """超过一定的阈值H持续N个周期"""
    pass


def e006(factor_series, cur_date, config):
    """M周期均线和N周期均线的差，判断趋势"""
    long_count = config["long_count"]
    short_count = config["short_count"]
    std_count = config["std_count"]
    end_num = len(factor_series[factor_series.index <= cur_date]) - 1
    long_start_num = end_num - long_count + 1
    if long_start_num < 0:
        return None
    long_mean = factor_series.iloc[long_start_num:end_num + 1].mean()
    short_start_num = end_num - short_count + 1
    short_mean = factor_series.iloc[short_start_num:end_num + 1].mean()
    std = factor_series.iloc[long_start_num:end_num - 1].std()
    event_value = short_mean - long_mean - std_count * std
    return event_value


def e007(factor_series, cur_date, config):
    """
    RSI：N日RSI=[A÷(A+B)]×100%；
    公式中，A——N日内收盘涨幅之和；
    B——N日内收盘跌幅之和(取正值)；
    N日RSI=100-100/(1+RS)
    :param factor_series: 
    :param cur_date: 
    :param config: 
    :return: 
    """


def rank_limit(factor_series, cur_date, up_rank, period=1):
    """
    排名阈值事件
    :param factor_series: 
    :param cur_date: 
    :param up_rank: 
    :return: 
    """
    # 找到当前日期
    # 找到当前日期或者与当前日期最相近的前一个日期
    his_end_num = len(factor_series[factor_series.index < cur_date]) - 1
    # 开始计算信号的大小
    gap = up_rank - factor_series.iloc[his_end_num]
    return gap


def case():
    data_index = pd.date_range('2010-1-1', end='2010-2-1', freq='D')
    series = pd.Series(data=range(len(data_index)), index=data_index)
    print(series)
    print(e002x1(factor_series=series, cur_date=data_index[10], config={"his_count": 3, "threshold": 0.2}))


def case_e000():
    pass


def case_e001():
    pass


if __name__ == "__main__":
    case()
