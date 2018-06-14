# -*- coding: utf-8 -*-
import os
import sys
import logging

logger = logging.getLogger('infocorecommon.IPMI')

# 设置IPMItool.exe的路径
IPMITool = r'{}\InfoCoreTools\bmc\ipmitool.exe'.format(os.path.dirname(os.path.abspath(sys.argv[0])))


def power_on(ip, username, password):
    if os.path.exists(IPMITool):
        logging.debug(r'ipmitool:{}打开电源'.format(ip))
        cmd = r'"{}" -I lanplus -H "{}" -U "{}" -P "{}" chassis power on 2>nul'.format(IPMITool, ip, username, password)
        logging.debug('运行命令行为：{}'.format(cmd))
        output = os.popen(cmd).read()
        if output.find(r'Error: Unable to establish IPMI v2 / RMCP+ session') != -1:
            logging.debug('IPMI工具运行失败，用户名密码错误，如果错误返回时间较长可能是未启用LAN上的IPMI')
            return None
        return output
    else:
        logger.debug(r'IPMItool.exe未找到，确认路径{}是否正确'.format(IPMITool))
        return None


def power_off(ip, username, password):
    if os.path.exists(IPMITool):
        logging.debug(r'ipmitool:{}关闭电源'.format(ip))
        cmd = r'"{}" -I lanplus -H "{}" -U "{}" -P "{}" chassis power off 2>&1'.format(IPMITool, ip, username, password)
        logging.debug('运行命令行为：{}'.format(cmd))
        output = os.popen(cmd).read()
        if output.find(r'Error: Unable to establish IPMI v2 / RMCP+ session') != -1:
            logging.debug('IPMI工具运行失败，用户名密码错误，如果错误返回时间较长可能是未启用LAN上的IPMI')
            return None
        return output
    else:
        logger.debug(r'IPMItool.exe未找到，确认路径{}是否正确'.format(IPMITool))
        return None


def power_status(ip, username, password):
    if os.path.exists(IPMITool):
        output = os.popen(
            r'{} -I lanplus -H {} -U {} -P {} chassis power status 2>nul'.format(IPMITool, ip, username, password))
        state = output.read().strip('\n')
        if state == 'Chassis Power is on':
            return 1
        elif state == 'Chassis Power is off':
            return 0
        else:
            return -1
    else:
        logger.debug(r'IPMItool.exe未找到，确认路径{}是否正确'.format(IPMITool))
        return None
