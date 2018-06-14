'''
三因子模型更新主程序
'''
import os
import pandas as pd
from openpyxl import load_workbook
import pyfi.DSfunctions as dsf
import pyfi.IVA_idx as ii
from pyfi import WindHelper
from datetime import datetime

begin_date = datetime(1990, 1, 1)
end_date = datetime(2018, 6, 1)
# ip_yoy = WindHelper.edb(codes=["ip_yoy","ip_cyoy"], begin_date=begin_date, end_date=end_date)

cf = os.getcwd()
IVAyoy = pd.read_excel(cf + '/四因子模型V9.xlsx', sheet_name='Data_宏观环境月频', index_col=[0], skiprows=[0]).iloc[:, 0]
IVAyoyc = pd.read_excel(cf + '/四因子模型V9.xlsx', sheet_name='Data_宏观环境月频', index_col=[0], skiprows=[0]).iloc[102:, 1]
RVol = pd.read_excel(cf + '/四因子模型V9.xlsx', sheet_name='Data_流动性+利率', index_col=[0], skiprows=[0]).iloc[:, -1]
Base = pd.read_excel(cf + '/四因子模型V9.xlsx', sheet_name='Data_宏观环境月频', index_col=[0], skiprows=[0]).iloc[:, -1].dropna(
    how='all')

IVAyoyr = pd.DataFrame(1 + IVAyoy)
IVAyoycr = pd.DataFrame(1 + IVAyoyc)
Base = ii.mean_Jan_Feb(Base)  # 平均基值的1、2月数据

# -----还原工业增加值绝对值-----
IVA_idx = ii.get_idx(IVAyoyr, IVAyoycr, Base)

# -----季节性调整-----
RVol_Deseason = dsf.Deseason(RVol.dropna(how='all'), Jan_Feb=False)
IVA_Deseason = dsf.Deseason(IVA_idx.iloc[:, 0].dropna(how='all'), Jan_Feb=False)
yoy_Deseason = (IVA_Deseason / IVA_Deseason.shift(12) - 1).dropna(how='all')

# -----Output-----
op = pd.DataFrame(index=pd.date_range(yoy_Deseason.index[0], RVol_Deseason.index[-1], freq='M'))
op['季调工业增加值当月同比'] = yoy_Deseason
op['季调R007波动率'] = RVol_Deseason

op.plot()
import matplotlib.pylab as plt
plt.show()
# op.to_excel(cf+'/季调结果.xlsx')
