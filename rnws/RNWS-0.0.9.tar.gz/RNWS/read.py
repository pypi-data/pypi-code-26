# -*- coding: utf-8 -*-
"""
Created on Thu May  3 17:21:35 2018

@author: yili.peng
"""

import pandas as pd
import time
import os
import pkg_resources

class reading_data:
	trading_dt_path = pkg_resources.resource_filename('RNWS', 'data/trading_date.csv')
	trading_dt=pd.read_csv(trading_dt_path,header=None)[0]

print('trading dt from %d to %d , if not enough please update'%(min(reading_data.trading_dt),max(reading_data.trading_dt)))

def read_df(path,file_pattern,start=None,end=None,inx_col=0,header=None,dat_col=1,**kwargs):
    '''
    if header is None, dat_col must be int
    otherwise dat_col shall be str or list
    '''
    t0=time.time()
    dt_range=reading_data.trading_dt
    if (start is not None):
        dt_range=dt_range[int(start)<=dt_range]
    if (end is not None):
        dt_range=dt_range[int(end)>=dt_range]
    if (type(dat_col) is str) or (type(dat_col) is int):
        result=pd.DataFrame()
        for dt in dt_range.tolist():
            file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
            if os.path.exists(file):
                try:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='gbk',**kwargs)[dat_col].rename(dt)
                except UnicodeDecodeError:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='utf_8',**kwargs)[dat_col].rename(dt)
                result=result.append(r)
            else:
                pass
        t1=time.time()
        print('reading finished --- time %0.3f s'%(t1-t0))
        return result.sort_index()
    elif (type(dat_col) is list) or (type(dat_col) is tuple):
        result=[pd.DataFrame() for i in range(len(dat_col))]
        for dt in dt_range.tolist():
            file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
            if os.path.exists(file):
                try:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='gbk',**kwargs)
                except UnicodeDecodeError:
                    r=pd.read_csv(file,header=header,index_col=inx_col,encoding='utf_8',**kwargs)
                for i in range(len(dat_col)):
                    result[i]=result[i].append(r[dat_col[i]].rename(dt))
            else:
                pass
        t1=time.time()
        print('reading finished --- time %0.3f s'%(t1-t0))
        return [r.sort_index() for r in result]
    else:
        raise Exception('wrong dat_col type')
	
def read_srs(path,file_pattern,start=None,end=None,header=None,data_col=1,**kwargs):
	t0=time.time()
	dt_range=reading_data.trading_dt
	if (start is not None):
		dt_range=dt_range[int(start)<=dt_range]
	if (end is not None):
		dt_range=dt_range[int(end)>=dt_range]
	result=pd.Series()
	for dt in dt_range.tolist():
		file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
		if os.path.exists(file):
			try:
				r=pd.read_csv(file,header=header,index_col=0,encoding='gbk',**kwargs)[data_col].tolist()
			except UnicodeDecodeError:
				r=pd.read_csv(file,header=header,index_col=0,encoding='utf_8',**kwargs)[data_col].tolist()
			result.at[dt]=r
		else:
			pass
	t1=time.time()
	print('reading finished --- time %0.3f s'%(t1-t0))
	return result.sort_index()
	
def read_dict(path,file_pattern,start=None,end=None,index_col=0,**kwargs):
    t0=time.time()
    dt_range=reading_data.trading_dt
    if (start is not None):
        dt_range=dt_range[int(start)<=dt_range]
    if (end is not None):
        dt_range=dt_range[int(end)>=dt_range]
    result={}
    for dt in dt_range.tolist():
        file=path+'\\'+file_pattern+'_'+str(dt)+'.csv'
        if os.path.exists(file):
            try:
                r=pd.read_csv(file,index_col=index_col,encoding='gbk',**kwargs)
            except UnicodeDecodeError:
                r=pd.read_csv(file,index_col=index_col,encoding='utf_8',**kwargs)
            result[dt]=r.sort_index()
        else:
            pass
    t1=time.time()
    print('reading finished --- time %0.3f s'%(t1-t0))
    return result