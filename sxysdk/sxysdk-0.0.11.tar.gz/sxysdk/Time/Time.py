# -*- coding:utf-8 -*-
import socket
import http.client
import logging
import datetime
import re

logger = logging.getLogger('root.InfoCoreTools.Time')

from InfoCoreTools.SSH import ssh
from InfoCoreTools.PsExc64 import windows_do_cmd

def getCurrentDatetimeString(suffix):
    logger.debug(r'get_date_time_string:获取当前时间')
    currentTime = datetime.datetime.now()
    currentTimeString = r"%04d%02d%02d%02d%02d" % (currentTime.year,
                                                       currentTime.month,
                                                       currentTime.day,
                                                       currentTime.hour,
                                                       currentTime.minute)
    currentTimeString = '{}-{}'.format(currentTimeString,suffix)
    return currentTimeString

def get_beijin_time_str():
    logging.info("准备获取北京时间")
    try:
        conn = http.client.HTTPConnection("www.beijing-time.org")
        conn.request("GET", "/time15.asp")
        response = conn.getresponse()
        if response.status == 200:
            result = response.read()
            result = result.decode('gbk')
            data = result.split(';\r\n')
            year = data[1].split('=')[1]
            month = data[2].split('=')[1]
            day = data[3].split('=')[1]
            wday = data[4].split('=')[1]
            hrs = data[5].split('=')[1]
            minute = data[6].split('=')[1]
            sec = data[7].split('=')[1].split(';')[0]
            beijin_time_str = "%s-%s-%s %s:%s:%s" % (year, month, day, hrs, minute, sec)
            logging.info('北京时间为:{}'.format(beijin_time_str))
            return beijin_time_str,True
    except socket.gaierror:
        return '[Errno 11001] getaddrinfo failed',False
    except Exception:
        logging.exception('未知错误')
        return None,False

def get_local_time_str():
    logging.info('准备获取本地时间')
    currentTime = datetime.datetime.now()
    currentTime_str = '{}-{}-{} {}:{}:{}'.format(currentTime.year,
                                                 currentTime.month,
                                                 currentTime.day,
                                                 currentTime.hour,
                                                 currentTime.minute,
                                                 currentTime.second)
    return currentTime_str,True

def get_linux_time_str(ip, username, password):
    try:
        logging.info('准备获取{}的系统时间'.format(ip))
        day_dict = {'Jan': 1,
                    'Feb': 2,
                    'Mar': 3,
                    'Apr': 4,
                    'May': 5,
                    'June': 6,
                    'Jun': 6,
                    'July': 7,
                    'Jul': 7,
                    'Aug': 8,
                    'Sept': 9,
                    'Sep': 9,
                    'Oct': 10,
                    'Nov': 11,
                    'Dec': 12}
        cmd = 'date -R'
        port = 22
        output,flag = ssh(ip,port,username,password,cmd)
        if flag:
            output = output.split(' ')
            wday = output[0].split(',')[0]
            day = output[1]
            day = re.sub(r"\b0*([1-9][0-9]*|0)", r"\1", day)    #去掉字符串前导0
            month = day_dict[output[2]]
            year = output[3]
            hrs = output[4].split(':')[0]
            minute = output[4].split(':')[1]
            sec = output[4].split(':')[2]
            linux_time_str = "%s-%s-%s %s:%s:%s" % (year, month, day, hrs, minute, sec)
            logging.info('{}的系统时间为:{}'.format(ip,linux_time_str))
            return linux_time_str,True
        else:
            logging.error('ssh错误')
            return 'ssh_error',False
    except BaseException:
        logging.exception('位置错误')
        return None,False

def get_windows_time_str(ip, username, password):
    try:
        logging.info('准备获取{}的系统时间'.format(ip))
        cmd = 'echo %date% %time%'
        output = windows_do_cmd(ip,username,password,cmd)
        if output == None:
            return r'未知错误windows_do_cmd'
        else:
            output = output.split(' ')
            i = 0
            while 1:
                try:
                    if output[i] == ' ':  # 列表中删除所有的' '元素
                        output.pop(i)
                    else:
                        i = i + 1
                except IndexError:
                    break
            logging.info('[get_windows_time_str]:{}'.format(output))
            year = output[0].split('/')[0]
            month = output[0].split('/')[1]
            day = output[0].split('/')[2]
            hrs = output[2].split(':')[0]
            minute = output[2].split(':')[1]
            sec = output[2].split(':')[2].split('.')[0]
            windows_time_str = "%s-%s-%s %s:%s:%s" % (year, month, day, hrs, minute, sec)
            logging.info('{}的系统时间为:{}'.format(ip,windows_time_str))
            return windows_time_str,True
    except IndexError:
        logging.info('无法获取{}系统时间.[{}]'.format(ip,output))
        return '系统时间获取失败', False
    except BaseException:
        logging.exception("未知错误")
        return '未知错误',False

def time_minus(time1, time2):
    logging.info('[time_minus]{} {}'.format(time1,time2))
    try:
        t1 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return time1
    try:
        t2 = datetime.datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return time2

    if t1 >= t2:
        delta=(t1-t2).seconds
    elif t2 > t1 :
        delta = - (t2 - t1).seconds
    return delta


def set_windows_time(ip, username, password, time_str):
    try:
        time_str = time_str.split(' ')
        date = time_str[0].replace('-','/')
        time = time_str[1]
        cmd = "date {} & time {}".format(date,time)
        windows_do_cmd(ip, username, password, cmd)
    except BaseException:
        logging.exception("未知错误")

def set_linux_time(ip, username, password, time_str):
    try:
        cmd = "date -s '{}'".format(time_str)
        port = 22
        output,flag = ssh(ip,port,username,password,cmd)
        cmd = 'clock -w'
        output, flag = ssh(ip, port, username, password, cmd)
    except BaseException:
        logging.exception('未知错误')