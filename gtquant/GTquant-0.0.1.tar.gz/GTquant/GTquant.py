# -*- coding: utf-8 -*-
"""
Created on Thu May 24 08:34:02 2018

@author: Hans Wang
@email: hans_wang@outlook.com
"""
import copy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tushare as ts

class Bar:
    """储存K线数据
    
    属性：
        self.symbol: 储存股票代码
        self.datetime: K线时间
        self.open: K线开盘价
        self.high: K线最高价
        self.low: K线最低价
        self.close: K线收盘价
        self.volume: K线成交量
    
    方法：
        self.update: 按传入数据更新bar
    
    """
    def __init__(self, symbol=None, datetime=None, open_price=None, high=None, low=None, close=None, volume=None):
        """初始化Bar实例，属性默认为None
        
        参数：
            datetime: K线时间
            open: K线开盘价
            high: K线最高价
            low: K线最低价
            close: K线收盘价
            volume: K线成交量
        
        """
        self.symbol = symbol
        self.datetime = datetime
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
    def update(self,symbol=None, datetime=None, open_price=None, high=None, low=None, close=None, volume=None):
        """更新Bar实例属性，如果更新时，某属性未传入，则将其修改为None
        
        参数：
            datetime: K线时间
            open: K线开盘价
            high: K线最高价
            low: K线最低价
            close: K线收盘价
            volume: K线成交量
        """
        self.symbol = symbol
        self.datetime = datetime
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
        
class TushareDataSource:
    """从tushare中提取日频K线数据
    
    属性：
        self.start_datetime: 数据的起始时间
        self.end_datetime: 数据的终止时间
        self.symbol: 股票代码
        self.bar: 记录K线数据的Bar实例，TushareDataSource实例初始化时自动创建
    接口：
        self.event_bar:运行start_getting_data_from_tushare时调用
    
    方法:
        self.start_getting_data_from_tushare: 从tushare中获取指定时间段的日频数据，进行循环对每日K线数据更新到bar实例
            中，然后使用event_bar接口进行处理
            
    """
    def __init__(self, start_datetime, end_datetime, symbol):
        """初始化TushareDataSource实例
        
        创建过程中，接口默认为None；创建Bar实例给self.bar属性
        
        参数：
            start_datetime: 数据的起始时间
            end_datetime: 数据的终止时间
            symbol: 股票代码
            
        """
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.symbol = symbol
        # bar对象创建
        self.bar = Bar()
        # 接口
        self.event_bar = None
    
    def start_getting_data_from_tushare(self):
        """从tushare获取数据，获取数据后将按顺序循环提取一条bar数据，更新给bar对象，同时运行event_bar进行回测
    
        """
        # 打印回测信息
        print('start getting data from tushare')
        print('symbol: ', str(self.symbol))
        print('start_datetime: ', self.start_datetime)
        print('end_datetime: ', self.end_datetime)
        print('*'*30)
        print('*'*30)
        
        # 获取数据
        self.data = ts.get_k_data(code=self.symbol, start=self.start_datetime, end=self.end_datetime)
        
        # 对于获取的数据，对其进行循环，由此模拟实盘中每日行情更新的状态
        for i, data_i in self.data.iterrows():
            
            # 对于每一个获得的新数据，将其更新到bar对象实例中。
            self.bar.update(
                symbol=data_i['code'],
                datetime=data_i['date'], 
                open_price=data_i['open'], 
                high=data_i['high'],
                low=data_i['low'],
                close=data_i['close'],
                volume=data_i['volume'],
            )
            
            # 检查接口是否完成拼接
            if self.event_bar is None:
                raise 
            # 如果完成拼接，则在更新bar后，对bar进行event_bar处理。
            self.event_bar(self.bar)
            
            
class Strategy:
    """用于实现回测的策略逻辑
    
    在self.on_bar中编写主要策略逻辑，配合self.send_order发送订单。
    可通过self.get_position self.get_cash_account获取当前持仓账户和现金账户信息。
    
    接口：
        self.event_send_order: 发送订单到其他系统
        self.event_get_cash_account: 从其他系统获取cash_account信息 
        self.event_get_position: 从其他系统获取position信息
    
    """
    def __init__(self):
        """初始化Strategy对象，设置各接口为None
        
        """
        self.event_send_order = None
        self.event_get_cash_account = None
        self.event_get_position = None
    
    def on_bar(self, bar):
        """
        策略实现主要逻辑实现，对bar进行处理
        """
        pass
    
    
#     # 处理事件
#     def on_event(self, message)
#         pass
    
    def send_order(self, symbol, datetime, price, volume, is_buy):
        """在on_bar中使用，用于发送订单
        
        参数：
            symbol: 股票代码
            datetime: 时间
            price: 挂单价
            volume: 交易量
            is_buy: 是否为买单
        """
        # 检查交易量是否大于0，避免交易量为0，或者为负产生无效订单
        if volume>0:
            order = Order(symbol, datetime, price, volume, is_buy)
            # 发送订单到其他系统进行后续处理
            self.event_send_order(order)
    
    def get_cash_account(self):
        """获取现金账户对象
        """
        # 检查接口是否拼接
        if self.event_get_cash_account is None:
            raise
            
        return self.event_get_cash_account()
        
    def get_position(self):
        """获取持仓账户对象
        """
        # 检查接口是否拼接
        if self.event_get_position is None:
            raise
        
        return self.event_get_position()


class Order:
    """记录订单信息用于后续撮合
    
    属性：
        self.symbol: 股票代码
        self.datetime: 发送订单的时间
        self.price: 挂单价
        self.volume: 交易量
        self.is_buy: 是否为买单
        
        self.cash_available: 从账户可用资金角度，该订单是否资金足够，默认为False
        self.position_available: 从账户可用仓位角度，该订单是否仓位足够，默认为False
        
        self.deal_price: 成交价
    """
    def __init__(self, symbol, datetime, price, volume, is_buy):
        """初始化Order实例
        
        参数：
            symbol: 股票代码
            datetime: 发送订单时间
            price: 挂单价
            volume: 交易量
            is_buy: 是否为买单
            
        """
        self.symbol = symbol
        self.datetime = datetime
        self.price = price
        self.volume = volume
        self.is_buy = is_buy
        
        self.cash_available = False
        self.position_available = False
        self.deal_price = None
    # 现在把获取接口假设由属性获取
    # 后续可通过重新构建Order的继承结构，使其可以适应期权交易。  


class CashAccount:
    """记录当前账户资金情况
    
    属性：
        self.cash: 记录账户资金情况
        self.cash_available：记录账户资金情况，用于AccountSystem验证订单是否可成交
        
    方法：
        self.reset_cash_available：重置cash_available为当前cash相同值
    """
    def __init__(self, initial_cash):
        self.cash = initial_cash
        
    def reset_cash_available(self):
        """重置cash_available，该属性用于从账户角度检查订单是否可发出
        """
        self.cash_available = copy.copy(self.cash)         
            
        
class PositionAccount:
    """记录当前账户持仓情况
    
    属性：
        self.position: 记录账户持仓情况
        self.position_available: 记录账户持仓情况，用于AccountSystem验证订单是否可成交
        
    方法:
        self.reset_position_available: 重置position_available为当前position相同值
    """
    def __init__(self):
        """初始化PositionAccount对象
        """
        self.position = {}
        # 暂时不允许有初始持仓
    
    def reset_position_available(self):
        """重置position_available，该属性用于从账户角度检查订单是否可发出
        """
        self.position_available = copy.copy(self.position)
        
        
class AccountSystem:
    """负责从账户角度检查订单是否可成交，根据撮合后订单更新账户信息
    
    支持Stragegy对象获取现金账户和持仓账户对象
    
    属性：
        self.cash_account:资金账户
        self.position_account:持仓账户
        
    接口：
        self.event_calculate_and_record_strategy_index: 其他系统计算并记录产品净值
        self.event_add_trade_record: 其他系统记录成交单
        
    方法：
        self.check_order_to_be_handled: 从资金和仓位角度检查订单是否可成交
        self.update_cash_account_and_position: 根据成交的订单更新账户
        self.update_cash_account_and_position_for_one_order: 实现具体成交的订单更新账户信息的逻辑
        
    """
    def __init__(self, initial_cash):
        """初始化AccountSystem类，创建CashAccount、PositionAccount对象
        
        参数：
            initial_cash: 策略回测初始资金
        """
        # CashAccount、PositionAccount对象创建
        self.cash_account = CashAccount(initial_cash)
        self.position_account = PositionAccount()
        # 接口
        self.event_calculate_and_record_strategy_index = None
        self.event_add_trade_record = None
        
    def check_order_to_be_handled(self, order_to_be_handled):
        """对暂存订单进行第一步检查（第二步成交价确认见DealPriceMatchingSystem），
        从账户角度判断买单是否有足够资金，卖单是否有足够仓位
        
        参数：
            order_to_be_handled: 待处理的订单池
        """
        # 重置cash_available和position_available属性，用于当次订单检查
        self.cash_account.reset_cash_available()
        self.position_account.reset_position_available()
        
        # 从账户角度检查订单是否可发出
        for order_i in order_to_be_handled:
            
            # 处理买单
            if order_i.is_buy:
                self.cash_account.cash_available -= order_i.price*order_i.volume
                if self.cash_account.cash_available >= 0:
                    order_i.cash_available = True
                else:
                    # 此处可接strategy.on_event
                    pass
                
            # 处理卖单    
            else:
                self.position_account.position_available[order_i.symbol] = (
                                   self.position_account.position_available.get(order_i.symbol, 0) - order_i.volume)
                if self.position_account.position_available[order_i.symbol] >= 0:
                    order_i.position_available = True
                else:
                    # 此处可接strategy.on_event
                    pass
    
    def update_cash_account_and_position(self, order_to_be_handled):
        """依据确定成交价的订单池循环对资金和持仓账户进行更新，更新时从暂存订单池中删除已处理订单
        
        参数：
            order_to_be_handled: 待处理的订单池
        """
        # 依据已确认成交价的订单池更新账户中资金和仓位信息
        for i in range(len(order_to_be_handled)):
            # 从订单池中按订单发送顺序处理订单，并将订单从订单池中移除
            order_i = order_to_be_handled.pop(0)
            # 根据订单更新账户信息
            self.update_cash_account_and_position_for_one_order(order_i)
        
        # 如果订单池未被清空，则报错
        if order_to_be_handled:
            raise
        
        # 计算策略指数，并由Recorder记录
        self.calculate_and_record_strategy_index()
        
    
    def update_cash_account_and_position_for_one_order(self, order):
        """依据单个订单对资金和持仓账户进行更新
        
        参数：
            order: 待处理订单
        """
        # 根据买单更新资金与持仓账户
        if order.is_buy and order.cash_available:
            # 更新资金账户
            self.cash_account.cash -= order.deal_price*order.volume
            # 更新持仓账户
            self.position_account.position[order.symbol] = self.position_account.position.get(order.symbol, 0) + order.volume
            # 记录order
            self.event_add_trade_record(order)
            # 打印成交信息
            print('datetime: ', order.datetime)
            print('BUY order accomplished')
            print('symbol: ', order.symbol)
            print('deal price: ', order.deal_price)
            print('volume', order.volume)
            print('-'*25)
        
        # 根据卖单更新资金与持仓账户
        elif (not order.is_buy) and order.position_available:
            # 更新资金账户
            self.cash_account.cash += order.deal_price*order.volume
            # 更新持仓账户
            self.position_account.position[order.symbol] = self.position_account.position.get(order.symbol, 0) - order.volume
            # 记录order
            self.event_add_trade_record(order)
            # 打印成交信息
            print('datetime: ', order.datetime)
            print('SELL order accomplished')
            print('symbol: ', order.symbol)
            print('deal price: ', order.deal_price)
            print('volume', order.volume)
            print('-'*25)
        else:
#             print('no trading happened')
            pass

    def calculate_and_record_strategy_index(self):
        """计算策略指数，并由recorder完成记录
        """
        # 获取当前账户中资金和持仓信息
        cash = self.cash_account.cash
        position = self.position_account.position
        
        # 检查接口是否拼接
        if self.event_calculate_and_record_strategy_index is None:
            raise
        self.event_calculate_and_record_strategy_index(cash, position)
        
    
    def get_cash_account(self):
        """为Strategy类提供查询现金账户服务
        """
        return self.cash_account
    
    def get_position(self):
        """为Strategy类提供查询持仓账户服务
        """
        return self.position_account
    
    
class DealPriceMatchingSystem:
    """用于确定每个订单的成交价
    """
    def __init__(self):
        """初始化DealPriceMatchingSystem对象
        """
        pass
    
    def confirm_deal_price(self, order_to_be_handled, bar):
        """确认订单成交价，此处假设订单以收盘价成交
        
        参数：
            order_to_be_handled: 待确定收盘价的订单池
            bar: bar数据
        """
        for order_i in order_to_be_handled:
            order_i.deal_price = bar.close   
        
        
class Recorder:
    """记录策略净值及交易记录
    
    属性：
        self.initial_cash: 策略初始资金
        self.strategy_index: 策略净值
        self.trade_record: 交易记录
        
    方法：
        self.record_latest_price: 记录最新价格，用于计算当前持仓股票的最新价值
        self.calculate_and_record_strategy_index: 计算并记录产品净值
        self.add_trade_record: 记录成交记录
    """
    def __init__(self, initial_cash):
        """初始化Recorder对象
        
        参数：
            initial_cash: 策略初始资金
        """
        self.initial_cash = initial_cash
        # 用于储存策略净值
        self.strategy_index = pd.Series()
        # 用于储存交易记录
        self.trade_record = []
        
    def record_latest_price(self, bar):
        """记录最新bar数据，用于计算策略指数
        
        参数：
            bar: 最新k线数据
        """
        self.bar = bar

    def calculate_and_record_strategy_index(self, cash, position):
        """计算策略指数并储存(AccountSystem类中使用)
        
        参数：
            cash: 账户更新前账户内现金
            position: 账户更新前账户内持仓
        """
        # 计算策略净值
        self.strategy_index[self.bar.datetime] = (cash + position.get(self.bar.symbol, 0)*self.bar.close)/self.initial_cash
        
    def add_trade_record(self, order):
        """储存交易记录(AccountSystem类中使用)
        
        参数：
            order: 成交的订单
        """
        self.trade_record.append(order)        
        
        
class StrategyEvaluator:
    """策略评价
    
    方法：
        self.plot_strategy_index:绘制策略净值和benchmark对比图
    """
    def __init__(self):
        """初始化StrategyEvaluator对象
        """
        pass
    
    def plot_strategy_index(self, record, benchmark):
        """绘制策略指数和基准的对比图
        
        参数：
            record: record类
            benchmark: 基准数据
        """
        sns.set_style('whitegrid')
        plt.figure(figsize=(10, 7))
        plt.plot(record.strategy_index, label='strategy')
        plt.plot((benchmark.pct_change()+1).cumprod(), label='benchmark')
        plt.legend(fontsize='large')
        plt.xticks(range(0,len(record.strategy_index), len(record.strategy_index)//10), rotation=45, fontsize='large')
        plt.yticks(fontsize='large')
        plt.title('strategy index and benchmark', fontsize='x-large')  
        plt.show()
        
        
class BackTester:
    """策略回测总控
    
    属性：
        self.data_source: 数据源对象
        self.strategy: 策略对象
        self.account_system: 账户对象
        self.deal_price_system: 撮合成交对象
        self.recorder: 记录者对象
        self.strategy_evaluator: 策略评价对象 
        self.order_to_be_handled: 待处理股票池
        self.start_datetime: 策略回测初始时间
		self.end_datetime: 策略回测终止时间
    方法：
        self.start_backtest: 开始策略回测
        self.assemble_backtest_system: 对回测中组件接口进行组合
        self.event_bar: 处理新到达bar数据
        self.buffer_order: 暂存订单
    """
    def __init__(self, start_datetime, end_datetime,  symbol, initial_cash, data_source, strategy):
        """初始化BackTester对象
        
        参数：
            start_datetime: 策略回测初始时间
            end_datetime: 策略回测终止时间
            symbol: 进行回测的股票代码
            initial_cash: 初始资金
            data_source: 数据源类
            strategy: 策略类
        """
        self.data_source = data_source(start_datetime, end_datetime, symbol)
        self.strategy = strategy
        self.account_system = AccountSystem(initial_cash)
        self.deal_price_matching_system = DealPriceMatchingSystem()
        self.recorder = Recorder(initial_cash)
        self.strategy_evaluator = StrategyEvaluator()
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.order_to_be_handled = []
        
    def start_backtest(self):
        """开始回测
        """
        # 组装接口
        self.assemble_backtest_system()
        # 开始获取数据并胡策
        self.data_source.start_getting_data_from_tushare()
        # 评价策略
        benchmark = ts.get_k_data('399300', self.start_datetime, self.end_datetime)['close']
        self.strategy_evaluator.plot_strategy_index(self.recorder, benchmark)
    
    def assemble_backtest_system(self):
        """组装接口
        """
        self.data_source.event_bar = self.event_bar
        self.strategy.event_send_order = self.buffer_order
        self.strategy.event_get_cash_account = self.account_system.get_cash_account
        self.strategy.event_get_position = self.account_system.get_position
        self.account_system.event_calculate_and_record_strategy_index = self.recorder.calculate_and_record_strategy_index
        self.account_system.event_add_trade_record = self.recorder.add_trade_record
    
    
    
    def event_bar(self, bar):
        """每次bar数据更新，都会由此函数完成策略回测主逻辑
        
        参数：
            bar： 新到达的bar数据
        """
        # recorder记录最新价
        self.recorder.record_latest_price(bar)
        # Strategy根据最新bar发送订单到订单暂存池
        self.strategy.on_bar(bar)
        # AccountSystem对订单暂存池中所有订单从账户角度判断资金或持仓是否足够，并对足够的进行标记
        self.account_system.check_order_to_be_handled(self.order_to_be_handled)
        # DealPriceMatchingSystem确认订单成交价
        self.deal_price_matching_system.confirm_deal_price(self.order_to_be_handled, bar)
        # AccountSystem对账户角度满足条件的订单，按照其成交价更新账户信息，同时Recorder记录订单，
        # 完成对所有订单对账户的更新后，Recorder记录当天策略指数数据
        self.account_system.update_cash_account_and_position(self.order_to_be_handled)
        
        

    def buffer_order(self, order):
        """将Strategy发送的订单暂存到self.order_to_be_handled
        
        参数：
            order: 新到达订单
        """
        self.order_to_be_handled.append(order)
        
        
        
        
        
        
        
        
        
        
        
        
        
        