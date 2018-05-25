#encoding=UTF-8
import sys
import os
import argparse
import numpy as np
import random
import logging
import logging.handlers
import argparse
import math
import glob
import time
import shutil

def init_log(args,logname):
   #LOG_FILE = './log/detector_mtcnn_fddb.log'
   LOG_FILE = './'+logname+'.log'
   
   handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 10*1024*1024, backupCount =10) # 实例化handler   
   fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
   formatter = logging.Formatter(fmt)   # 实例化formatter  
   handler.setFormatter(formatter)      # 为handler添加formatter  

   logger = logging.getLogger(logname)    # 获取名为tst的logger  
   logger.addHandler(handler)           # 为logger添加handler  
   logger.setLevel(logging.DEBUG)
   return logger
def parse_arguments(argv,argument_name_type_help_list):
    parser = argparse.ArgumentParser()
    for argument in argument_name_type_help_list:
        parser.add_argument(argument[0], type=argument[1], help=argument[2])
    #parser.add_argument('filelist_path', type=str, help='the path of the image file list.')
    #parser.add_argument('dst_path', type=str, help='the path of the detect result file.')
    return parser.parse_args(argv)
def log2(message,logger):
    message=change_arrange(message)
    logger.info(message)
    print message
def add_space(message):
    message=message.count(':')*'    '+message
    return message

def change_c(message):
    for i in range(0,len(message)):
        if message[i]==':':
            message='_'
    return message
def change_arrange(message):
    message=message.count(':')*'    '+''.join(message.split(':')[-2:])
    return message

def get_area(rec):
    #     author : zhaomingming 
    #    function: get the area of the rectangle
    # modify date: 20180508
    #     company: vipkid

    # input: rec,has 4 elements,
    # rec[0]  the x of topleft of the rectangle
    # rec[1]  the y of topleft of the rectangle
    # rec[2]  the x of bottomright of the rectangle 
    # rec[3]  the y of bottomright of the rectangle

    # output: area the area of the rec

    area=float(rec[3]-rec[1])*float(rec[2]-rec[0])
    return area

def get_score(pre_log_str,gt_rec,est_rec):
    #     author : zhaomingming 
    #    function: get the score for detection,the score is IOU
    # modify date: 20180508
    #     company: vipkid
    
    # input:
    #      gt_rec : the groundtruth rectangle
    #      est_rec : the estimation rectangle
    # output:
    #      score : the IOU score between gt_rec and est_rec

    pre_log_str+=sys._getframe().f_code.co_name+':'
    log2(pre_log_str+'[start]')
    intersected_rec=np.array((max(gt_rec[0],est_rec[0]),max(gt_rec[1],est_rec[1]),min(gt_rec[2],est_rec[2]),min(gt_rec[3],est_rec[3])))
    if intersected_rec[0]<intersected_rec[2] and intersected_rec[1]<intersected_rec[3]:
   
        inter_area=get_area(intersected_rec)
        jointed_area=get_area(gt_rec)+get_area(est_rec)-inter_area
        score=inter_area/jointed_area
    else:
        score=0
    log2(pre_log_str+'[  end]')
    return score
 


def readListfromFile(listfilepath,pre_log_str):
    #     author : zhaomingming 
    #    function: get list in the file 
    # modify date: 20180508
    #     company: vipkid
    
    # input:
    #     listfilepath : the path of the list file
    # output:
    #     filelist : the filelist with the python's list type 
    
    pre_log_str+=sys._getframe().f_code.co_name+':'
    log2(pre_log_str+'[start]')
    print listfilepath
    file_in=open(listfilepath)
    filelist=[]
    for line in file_in:
         print line
         filelist.append(line)
    log2(pre_log_str+'[ end ]')
    return filelist


