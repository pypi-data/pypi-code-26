# -*- coding:utf-8 -*- 
'''
Created on 04/05/2018
@author: Jimmy
'''

import requests
# from .authorize import Authorize
from bbindex.vars import *
from bbindex import base
import pandas as pd

session = requests.Session()

class DataAPI():
# class DataAPI(Authorize):
    def __init__(self, username='', password='', token=''):
        pass
#         Authorize.__init__(self, username, password, token, session)
        ### Authorize
#         self._authorize()
# 
#         if self._isvalid:
#             ### Do smt.
#             pass

    def getIndexes(self, index_name='', index_type=''):
        """
        Get bbindex list
        """
        index_name = '' if index_name is None else index_name
        index_type = '' if index_type is None else index_type
        if (index_name != '') & (index_type==''):
            params = GET_INDEXES%(index_name)
        elif (index_name == '') & (index_type != ''):
            params = GET_INDEXES%(index_type)
        elif (index_name != '') & (index_type != ''):
            params = GET_INDEXES%(index_name)
        else:
            params = GET_INDEXES%('')
        data = base.get_http_result(params)
        if (index_type != ''):
            data = base.to_df(data['data'], index=[0])
        else:
            data = base.to_df(data['data'])
        data = data[INDEX_COLS]
        data['timestamp'] = data['timestamp'].map(lambda x: int2time(x))
        return data
        
        
    def getIndex(self, index_name=''):
        """
        Get bbindex by index_name
        """
        if (index_name=='' or index_name is None):
            print(MSG_FOR_INPUT)
            return None
        params = GET_INDEX%(index_name)
        data = base.get_http_result(params)
        index = Index(index_name)
        ds = data['data']
        df = base.to_df(ds['comps'])
        index.comps = df
        index.name = ds['name']
        index.percent_change_seasonly_btc = ds['percent_change_seasonly_btc']
        index.value_usd= ds['value_usd']
        index.percent_change_24h_usd = ds['percent_change_24h_usd']
        index.percent_change_168h_btc = ds['percent_change_168h_btc']
        index.percent_change_168h_usd = ds['percent_change_168h_usd']
        index.description_cn = ds['description_cn']
        index.percent_change_monthly_usd = ds['percent_change_monthly_usd']
        index.percent_change_seasonly_usd = ds['percent_change_seasonly_usd']
        index.percent_change_monthly_btc = ds['percent_change_monthly_btc']
        index.percent_change_24h_btc = ds['percent_change_24h_btc']
        index.type = ds['type']
        index.value_btc = ds['value_btc']
        index.description = ds['description']
        return index
    
    
    def get_comps(self, index_name=''):
        if (index_name=='' or index_name is None):
            print(MSG_FOR_INPUT)
            return None
        data = self.getIndex(index_name)
        return data.comps
    
    
    def indexHistory(self, index_name='', length=''):
        if length is None:
            length = ''
        if (index_name=='' or index_name is None) & (length == '' or length is None):
            print(MSG_FOR_INPUT)
            return None
        params = GET_HISTORY_BYLENGTH%(index_name , length)
        data = base.get_http_result(params)
        df = pd.DataFrame(data['data']['vs'], columns=HISTORY_COLS)
        df['date'] = df['date'].map(lambda x: int2time(x))
        return df
    
    
    def listIndxCoins(self, index_name=''):
        """
        查询指数所包含的coin数据 :
        param:
        index_name 指数名称 :
        return 
                    返回指数中包含的代币数据数组
        """
        if index_name is None or index_name == '':
            print(MSG_FOR_INPUT)
            return None
        params = GET_INDEX_COINS%(index_name)
        data = base.get_http_result(params)
        data = base.to_df(data['data'])
        return data


class Index(object):
    def __init__(self, name):
        self.name = name

        
def int2time(timestamp):
    import time
    value = time.localtime(timestamp)
    dt = time.strftime('%Y-%m-%d %H:%M:%S', value)
    return dt

