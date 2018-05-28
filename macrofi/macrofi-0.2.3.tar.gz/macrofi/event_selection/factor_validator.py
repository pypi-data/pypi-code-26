# encoding: utf-8
from macrofi.event_selection import factor_event
from macrofi.event_selection.common import *
import numpy as np


def get_adj_factor_series(asset_series, factor_series, beginDate=None, endDate=None, lag=2):
    """根据时间序列提供所有可能的调仓时间(产生信号后承受波动的第一天), 是一个母集合，
    因为该函数没有调用事件，因此不知道事件有效时间是从什么时候开始的，
    所以我们无法确定策略回测的真正开始时间。
    具体回测调仓点还受到period,具体事件以及开始结束时间等因素影响
    为了保证策略回测的第一天就是事件信号产生的那天，beginDate只是一个必要条件，
    开始时间必然大于等于beginDate
       :param beginDate: 
       :param endDate: 
       :param asset_series: (series) 必须为日度数据
       :param factor_series: (series) 可以是日度，周度或者月度
       :param lag: (int) lag这个概念是一个比较精细化的概念,
       lag=2表示T-1得到的信息只能在T日收盘买入，
       T+1日才会出现资产的波动，比如一些基于资产价格的因子。
       但是对于一些宏观因子，我们仍然可以选择lag=2,
       因为虽然CPI等因子都是白天公布，资产在当日公布之后以收盘价买入，
       但是CPI公布的是上个月的数据，仍然差距lag=2。
       如果CPI在每个月的月末公布的是当周的数据，那么lag=1。
       :return: (Series)
    """
    # 筛选出开始时间到结束时间的区间
    if beginDate is not None:
        factor_series = factor_series[(factor_series.index >= beginDate)]
    elif endDate is not None:
        factor_series = factor_series[(factor_series.index <= endDate)]
    # 计算所以调仓时点
    general_adjust_time_spots = []
    corresponding_factors = []
    for i in range(len(factor_series) - 1):
        length = len(asset_series[asset_series.index < factor_series.index[i + lag - 1]]) + 1
        if length == 0:  # 资产时间序列第一项必然大于因子的第2项时间
            # 对于0 情况进行单独处理,如果资产的起始时间和因子事件产生时间相距在1/10个因子周期以内，则计入
            days_ = (asset_series.index[0] - factor_series.index[i + 1]).days
            if days_ <= (factor_series.index[1] - factor_series.index[0]).days / 10.0:
                general_adjust_time_spots.append(asset_series.index[0])
                corresponding_factors.append(factor_series[i])
        elif 0 < length < len(asset_series):  # len>0, 该调仓点在asset_series里面
            time_spot = asset_series.index[length]
            general_adjust_time_spots.append(time_spot)
            corresponding_factors.append(factor_series[i])
        else:
            break
    # print corresponding_factors
    adjust_factor_series = pd.Series(data=corresponding_factors,
                                     index=general_adjust_time_spots)
    adjust_factor_series.name = factor_series.name
    return adjust_factor_series


def get_adj_evt_val_series(asset_series, factor_series, event_name, config, beginDate=None, endDate=None, lag=2):
    """返回即时生效事件值的事件序列,该函数可以通过事件函数求得事件开始时间"""
    adj_factor_series = get_adj_factor_series(asset_series, factor_series, beginDate=beginDate, endDate=endDate,
                                              lag=lag)
    # 先确定要调用的事件
    # if event_name in event_dict:
    #     event = event_dict[event_name]
    # else:
    #     raise Exception(u"该因子事件还没有收录到因子事件库中，请更新你的因子事件库再重新运行！")
    #     # return None  # 返回空格表示事件名称没有定义
    try:
        event = getattr(factor_event, event_name)
    except:
        raise Exception(u"该因子事件还没有收录到因子事件库中，请更新你的因子事件库再重新运行！")
    # 进行周期化处理
    period = config["period"]
    event_values = []
    time_spots = []
    start_time_spot = None
    for i in range(len(adj_factor_series)):
        event_value = event(adj_factor_series, adj_factor_series.index[i], config)
        if event_value is None:
            continue
        else:
            if start_time_spot is None:
                start_time_spot = i
                event_values.append(event_value)
                time_spots.append(adj_factor_series.index[i])
            elif (i - start_time_spot) % period == 0:
                event_values.append(event_value)
                time_spots.append(adj_factor_series.index[i])
            else:
                continue
    adj_evt_val_series = pd.Series(data=event_values, index=time_spots)
    # adj_evt_val_series = pd.Series([event(adj_factor_series, adj_factor_series.index[i], config)
    #                                 for i in range(len(adj_factor_series))], index=adj_factor_series.index)
    adj_evt_val_series.name = adj_factor_series.name
    adj_evt_val_series.dropna(inplace=True)  # 去除前期无信号区域
    return adj_evt_val_series


def get_pos_series(adj_evt_val_series, relation, type_, short):
    position_series = pd.Series()
    if short:  # 可以做空，说明该资产为期货，无票息收益，不适宜长期持有
        if relation == POSITIVE:
            if type_ == UP:  # 正向且只有做多信号
                position_series = adj_evt_val_series.apply(lambda x: 1 if x > 0 else 0)
            elif type_ == DOWN:  # 正向且只有做空信号
                position_series = adj_evt_val_series.apply(lambda x: -1 if x < 0 else 0)
            elif type_ == ALL:
                position_series = adj_evt_val_series.apply(lambda x: (1 if x > 0 else 0) if x >= 0 else -1)
        elif relation == NEGATIVE:
            if type_ == UP:  # 负向且只有做空信号
                position_series = adj_evt_val_series.apply(lambda x: -1 if x > 0 else 0)
            elif type_ == DOWN:  # 负向且只有做多信号
                position_series = adj_evt_val_series.apply(lambda x: 1 if x < 0 else 0)
            elif type_ == ALL:
                position_series = adj_evt_val_series.apply(lambda x: (-1 if x > 0 else 0) if x >= 0 else 1)
        else:
            raise Exception(u"relation的值无法识别！")
    else:  # 不可做空,说明为现券指数，可长期持有
        if relation == POSITIVE:
            if type_ == UP:  # 正向且只有做多信号
                position_series = adj_evt_val_series.apply(lambda x: 1 if x > 0 else 0)
            elif type_ == DOWN:  # 正向且只有做空信号
                position_series = adj_evt_val_series.apply(lambda x: 0 if x < 0 else 1)
            elif type_ == ALL:
                position_series = adj_evt_val_series.apply(lambda x: (1 if x > 0 else 0) if x >= 0 else 0)
        elif relation == NEGATIVE:
            if type_ == UP:  # 负向且只有做空信号
                position_series = adj_evt_val_series.apply(lambda x: 0 if x > 0 else 1)
            elif type_ == DOWN:  # 负向且只有做多信号
                position_series = adj_evt_val_series.apply(lambda x: 1 if x < 0 else 0)
            elif type_ == ALL:
                position_series = adj_evt_val_series.apply(lambda x: 0 if x >= 0 else 1)
        else:
            raise Exception(u"relation的值无法识别！")
    position_series.name = "position"
    return position_series


def sharp_ratio_check(asset_series, factor_series, event_name, config, beginDate=None, endDate=None, lag=2, short=False):
    """
    对因子-因子事件进行回测，针对因子信号计算器夏普比率，主要评价因子信号的对称性特征。
    如果超额夏普比率大，说明因子-因子事件，无论是触发还是没被触发都可以作为一种做多或者做空的信号，
    注意：如果超额夏普比率不明显，不能说明因子无效。
    策略的开始时点就是信号产生的时点，特殊情况下，和最近的信号距离不超过因子周期的1/10
    :param beginDate: 
    :param endDate: 
    :param asset_series: 
    :param factor_series: 
    :param event_name: 
    :param config: 
    :param short: Boolean,默认False,即不允许做空
    :return: dict
    """
    adj_evt_val_series = get_adj_evt_val_series(asset_series, factor_series, event_name, config, lag=lag)
    # 读取配置文件相关信息
    type_ = config["type"]
    relation = config["relation"]
    position_series = get_pos_series(adj_evt_val_series, relation, type_, short)
    # period = config["period"]  # 调整周期(以因子单位周期为基准周期)
    df = adj_evt_val_series.to_frame(name=adj_evt_val_series.name)
    asset_ret_series = asset_series.pct()  # 转换成涨跌幅
    df = df.join(position_series, how="outer").join(asset_ret_series, how="outer")
    df.fillna(inplace=True, method="ffill")
    df = df.dropna()
    #  此时第一个事件信号产生日期已经确定，接下来要基于period对df事件值列进行再处理

    df.loc[:, "value"] = (df.loc[:, asset_ret_series.name] * df.loc[:, "position"] + 1).cumprod()
    df.loc[:, "base"] = (df.loc[:, asset_ret_series.name] + 1).cumprod()
    # 组建返回信息
    report = dict()
    report["sp"] = sharpe_ratio(df["value"])
    report["excess_sp"] = - sharpe_ratio(df["base"]) + report["sp"]
    report["ts"] = df
    return report


def perform_after_event(asset_series, factor_series, event_name, config, begin_date=None, end_date=None,
                        asset_price=True, lag=2):
    """单向因子检验。
    包括信息比率，最大回撤，等等
    
    :param asset_series: 
    :param factor_series: 
    :param event_name: 
    :param config: 
    :param begin_date: 
    :param end_date: 
    :param asset_price: string 默认True，如果是ytm则为False
    :param lag
    :return: 
    """
    adj_evt_val_series = get_adj_evt_val_series(asset_series, factor_series, event_name,
                                                config, begin_date, end_date, lag)
    relation = config["relation"]  # POSTIVE or NEGATIVE
    type_ = config["type"]
    if asset_price:  # 采用资产价格作为资产表征
        adj_ret_series = pd.Series(
            [asset_series.loc[adj_evt_val_series.index[i + 1]] / asset_series.loc[adj_evt_val_series.index[i]] - 1 for i
             in
             range(len(adj_evt_val_series) - 1)],
            index=adj_evt_val_series.index[:-1])
        adj_ret_series.name = "ret"
    else:  # 采用收益率作为资产表征
        adj_ret_series = pd.Series(
            [(asset_series.loc[adj_evt_val_series.index[i + 1]] - asset_series.loc[adj_evt_val_series.index[i]]) * 100
             for i
             in
             range(len(adj_evt_val_series) - 1)],
            index=adj_evt_val_series.index[:-1])
        adj_ret_series.name = "bp"
    df = pd.concat([adj_evt_val_series, adj_ret_series], axis=1)
    df = df.dropna()
    origin_ts = df
    if type_ == UP:  # 正值产生信号
        df = df[df[adj_evt_val_series.name] > 0]
    elif type_ == DOWN:  # 负值产生信号
        df = df[df[adj_evt_val_series.name] < 0]
    elif type_ == ALL:  # 正负值都产生信号,不处理
        pass
    else:
        raise Exception(u"The type in the config is illegal.")
    ir = df[adj_ret_series.name].mean() / df[adj_ret_series.name].std()
    report = dict()
    report["origin_ts"] = origin_ts
    report["ts"] = df
    report["ir"] = ir
    if relation == POSITIVE and asset_price:
        report["worst_perform"] = df[adj_ret_series.name].min()
    elif config["type"] == NEGATIVE and asset_price:
        report["worst_perform"] = df[adj_ret_series.name].max()
    elif config["type"] == POSITIVE and not asset_price:
        report["worst_perform"] = df[adj_ret_series.name].max()  # 收益率上行最多
    elif config["type"] == NEGATIVE and not asset_price:
        report["worst_perform"] = df[adj_ret_series.name].min()  # 收益率下行最多
    return report


def case1():
    from windhelper import WindHelper
    from datetime import datetime
    beginDate = datetime(2011, 1, 1)
    endDate = datetime(2017, 8, 22)
    para = "close"
    config = {"relation": NEGATIVE, "type": UP, "his_count": 12, "std_count": 0.5, "period": 1}
    df = WindHelper.getMultiTimeSeriesDataFrame(["060E.CS"], beginDate=beginDate, endDate=endDate,
                                                para=para)
    df = df.dropna()
    df.tail()
    factor_df = WindHelper.getMultiTimeSeriesDataFrame(["M0000612"], beginDate=beginDate, endDate=endDate,
                                                       para=para)
    factor_df = factor_df.dropna()
    config = {"period": 5, "relation": NEGATIVE, "type": UP, "his_count": 30, "threshold": 0}
    report2 = perform_after_event(df["060e.cs_close"], factor_df["m0000612_close"], "e002x1", config)


def case2():
    from windhelper import WindHelper
    from datetime import datetime, timedelta
    beginDate = datetime(2011, 1, 1)
    endDate = datetime(2017, 8, 22)
    para = "close"
    df = WindHelper.getEDBTimeSeriesDataFrame(["S0059749"], beginDate=beginDate, endDate=endDate)
    df = df.dropna()
    factor_df = WindHelper.getMultiTimeSeriesDataFrame(["M0000612"], beginDate=beginDate, endDate=endDate,
                                                       para=para)
    factor_df.index = factor_df.index - timedelta(days=10)
    config = {"relation": NEGATIVE, "type": UP, "his_count": 18, "std_count": 2, "period": 1}
    report = sharp_ratio_check(df.iloc[:,0], factor_df.iloc[:,0], "e001", config, lag=2)
    print(report)


if __name__ == "__main__":
    case2()
