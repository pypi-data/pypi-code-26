# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 15:58:17 2018

@author: yili.peng
"""


from .basic_functions import functions
from .check_validation import is_validate
from .df_gen import formula_gen
from RNWS import write
import warnings
from multiprocessing import Pool
from functools import partial
warnings.simplefilter('ignore')


def generate_one(name,df,**parms):
    for key in parms.keys():
        exec(key+'=parms[\''+key+'\']')
    found=False
    while not found:
        formula,df_new=formula_gen(name=name,frame_df=df)
        print(formula.equation)
        exec(formula.df_name+'='+formula.equation)
        if is_validate(eval(formula.df_name),parms):
            found=True
            print('\u2191\u2191\u2191 found \u2191\u2191\u2191')
    parms.update({formula.df_name:eval(formula.df_name)})
    return df_new,parms

def find_batch_name(df,name_start,batch_size):
    last_name=df['df_name'].iloc[-1]
    start_num=(int(''.join(list(filter(str.isdigit,last_name))))+1 if last_name.startswith(name_start) else 0)
    return [name_start+str(i) for i in range(start_num,start_num+batch_size)]

def generate_batch(df,batch_size,out_file_path,name_start,**parms):
    names=find_batch_name(df=df,name_start=name_start,batch_size=batch_size)
    parms_new=parms
    df_new=df
    d={}
    for name in names:
        df_new,parms_new=generate_one(name=name,df=df_new,**parms_new)
        d[name]=parms_new[name]
    write.write_factors(path=out_file_path,file_pattern='factor',**d)
    return df_new,parms_new

def generate_batch_mul(df,batch_size,out_file_path,name_start,processors=None,**parms):
    print('multiprocessing may generate duplicated factors')
    df_new=df
    parms_new=parms
    names=find_batch_name(df=df,name_start=name_start,batch_size=batch_size)    
    d={}
    pool=Pool(processes=processors)
    results=pool.map(partial(generate_one,df=df,**parms),names)
    pool.close()
    pool.join()
    for i in range(len(names)):
        df_tmp=results[i][0]
        parms_tmp=results[i][1]
        d[names[i]]=parms_tmp[names[i]]
        df_new=df_new.append(df_tmp.iloc[-1],ignore_index=True)
    parms_new.update(d)
    write.write_factors(path=out_file_path,file_pattern='factor',**d)
    return df_new,parms_new

