# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 22:04:45 2018

@author: jasonai
"""

import sys
import math
from pmipy import pmi
import numpy as np
import pandas as pd
from tqdm import tqdm
import multiprocessing as mp

def haversine(lng1, lat1, lng2, lat2): # 根据经纬度计算两点距离  
    lng1, lat1, lng2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])  
    dlng = lng2 - lng1   
    dlat = lat2 - lat1   
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2 
    c = 2 * math.asin(math.sqrt(a))   
    r = 6371 # 地球平均半径，单位为公里  
    d = c * r * 1000
    return d

# 此函数速度太慢，放弃使用
# 需输入点位经纬度数据，宜出行数据，其中宜出行的数据表头格式是标准格式
# df_ycx['distance'] = df_ycx.apply(lambda row: haversine(lng1, lat1,row['lng'], row['lat']), axis=1)此代码更耗时
def yichuxing_backup1(df_point, df_ycx, lnglat, meter=500):
    PF = []
    for lng1, lat1 in tqdm(df_point.loc[:, [lnglat]].values):
        peo_flow = 0 # 人流指数
        for lng2, lat2, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
            if haversine(lng1, lat1, lng2, lat2) <= meter:
                peo_flow += count
        PF.append(peo_flow)
        
    df_point['人流指数'] = PF
    return df_point

def run_task(df,df_ycx, lnglat, meter):
    PF = []
    for lng1, lat1 in tqdm(df.loc[:, lnglat].values):
        peo_flow = 0 # 人流指数
        for lng2, lat2, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
            #print(peo_flow)

            if haversine(lng1, lat1, lng2, lat2) <= meter:
                peo_flow += count
        PF.append(peo_flow)
    df['人流指数'] = PF
    return df
    #print('Task {0} end.'.format(name))

def yichuxing_backup2(df_point, df_ycx, lng, lat, meter, ncore=6):
    def tmp_func(df):
        PF = []
        for lng1, lat1 in tqdm(df.loc[:, [lng, lat]].values):
            peo_flow = 0 # 人流指数
            print(1)
            for lng2, lat2, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
                if haversine(lng1, lat1, lng2, lat2) <= meter:
                    peo_flow += count
            PF.append(peo_flow)
        df['人流指数'] = PF
        return df

    def apply_parallel(df_grouped, func):
        """利用 Parallel 和 delayed 函数实现并行运算"""
        results = Parallel(n_jobs=-1)(delayed(func)(group) for name, group in df_grouped)
        return pd.concat(results)
    nrow = len(df_point)
    df_point['grouping'] = np.arange(nrow) // (nrow / ncore)
    df_grouped = df_point.groupby('grouping')
    df_point =apply_parallel(df_grouped, tmp_func)
    return df_point

def yichuxing_backup3(df_point, df_ycx, lng, lat, meter, ncore=2):
    def proc(df):
        PF = []
        for lng1, lat1 in tqdm(df.loc[:, [lng, lat]].values):
            peo_flow = 0 # 人流指数
            # print(1)
            for lng2, lat2, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
                if haversine(lng1, lat1, lng2, lat2) <= meter:
                    peo_flow += count
            PF.append(peo_flow)
        df['人流指数'] = PF
        return df
    
    p = mp.Pool(ncore)
    split_dfs = np.array_split(df_point, ncore)
    pool_results = p.map(proc, split_dfs)
    p.close()
    p.join()
    df_all = pd.concat(pool_results)
    # pdt.assert_series_equal(parts['id'], big_df['id'])
    return df_all

@pmi.execInfo()
def getPeopleFlow(pointFile, ycxFile, lnglat=('经度','纬度'), meter='500', core_num='max', outputFile=''):
    # 读取店铺点数文件
    if pointFile[-4:] == '.csv':
        df_point = pd.read_csv(pointFile, engine='python')
    elif pointFile[-5:] == '.xlsx':
        df_point = pd.read_excel(pointFile)
    else:
        sys.exit('Please input csv or xlsx file!')
    # 读取宜出行数据文件，获取人流
    if ycxFile[-4:] == '.csv':
        df_ycx = pd.read_csv(ycxFile, engine='python')
    elif ycxFile[-5:] == '.xlsx':
        df_ycx = pd.read_excel(ycxFile)
    else:
        sys.exit('Please input csv or xlsx file!')
    
    # 输出文件名
    if not outputFile:
        outFile = pointFile + '_' + ycxFile + '_{}'.format(meter)
        outFile = outFile.replace('.csv', '')
        outFile = outFile.replace('.xlsx', '')
    # 获取经纬度表头列表
    lnglat = list(lnglat)
    meter = int(meter)
    # 确定并发使用的CPU线程数
    core_max = mp.cpu_count()
    if core_num != 'max':
        try:
            ncore = int(core_num)
            core_num = ncore if ncore <= core_max else core_max
        except ValueError:
            sys.exit('请输入正确的线程数(整数值)！')
    else:
        core_num = core_max
    
    df_split = np.array_split(df_point, core_num)
    p = mp.Pool(processes=core_num)
    funcList = []
    for df in df_split:
        f = p.apply_async(run_task, args=(df, df_ycx, lnglat, meter,))
        funcList.append(f)
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    resList = []
    for f in funcList:
        resList.append(f.get(timeout=0.5))
    df_all = pd.concat(resList)
    # 添加时间信息
    df_all['爬取时间'] = ycxFile.split('.')[0][-19:-3] # '南京2018-04-05-11-16-34.csv'格式
    df_all.to_excel(outFile+'.xlsx', index=False)
    print('All processes done!')


if __name__ == '__main__':
    pointFile = '江苏省linxdata_经纬度匹配最终版V1.xlsx'
    ycxFile = '南京2018-04-01-17-40-57.csv'
    getPeopleFlow(pointFile, ycxFile, lnglat, 500, 12, 'ts')
    
    
    