# -*- coding: utf-8 -*-
"""
Created on Thu May  3 17:51:39 2018

@author: yili.peng
"""

import time
import os
import pandas as pd

def write_df(df,path,file_pattern,**kwargs):
    '''
    dt*StkId
    '''
    t0=time.time()
    if not os.path.exists(path):
        os.makedirs(path)
    for inx in df.index:
        df.loc[inx].to_csv(path+'\\'+file_pattern+'_'+str(inx)+'.csv',**kwargs)
    t1=time.time()
    print('writing finished --- time %0.3f s'%(t1-t0))

def write_dict(dictionary,path,file_pattern,**kwargs):
    t0=time.time()
    if not os.path.exists(path):
        os.makedirs(path)
    for inx in dictionary.keys():
        dictionary[inx].to_csv(path+'\\'+file_pattern+'_'+str(inx)+'.csv',**kwargs)
    t1=time.time()
    print('writing finished --- time %0.3f s'%(t1-t0))

def write_factors(path,file_pattern,**kwargs):
    '''
    kwargs:{'f1':factor1,'f2':factor2,...}
    factor: dt*StkId
    '''
    t0=time.time()
    result_DF=pd.DataFrame({(outerKey, innerKey): values for outerKey, innerDict in kwargs.items() for innerKey, values in innerDict.items()})
    if not os.path.exists(path):
        os.makedirs(path)
    for inx in result_DF.index:
        result_DF.loc[inx].unstack(level=0).rename_axis('StkID').to_csv(path+'\\'+file_pattern+'_'+str(inx)+'.csv',encoding='gbk')
    t1=time.time()
    print('writing finished --- time %0.3f s'%(t1-t0))