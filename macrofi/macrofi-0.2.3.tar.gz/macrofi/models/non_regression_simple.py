# NRS 模型
from macrofi.data_agent import *

F = {get_shuini}
V = {get_crb}
T = {get_hs300, get_nhspzs}
# 获取数据
begin_date = datetime(2014, 1, 1)
end_date = datetime(2017, 1, 1)
## 基本面因子
Flist = []
for i in range(len(F)):
    pass
## 通胀因子
Vlist = []
for i in range(len(V)):
    pass
## 估值因子
Tlist = []
for i in range(len(T)):
    pass
## 技术情绪数据
# 数据标准化
# 因子事件化
# 多因子整合
# 策略回溯
import macrofi.data_agent

print(dir(macrofi.data_agent))


class NonRegressionSimple(object):
    def __init__(self, fund):
        pass


