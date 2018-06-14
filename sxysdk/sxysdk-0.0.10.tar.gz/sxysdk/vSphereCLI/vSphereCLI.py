# -*- coding: utf-8 -*-

import os
import sys
import logging
import re

logger = logging.getLogger('infocorecommon.vSphereCLI')
vSphereCLI = r'C:\Program Files (x86)\VMware\VMware vSphere CLI\bin\vmware-cmd.pl'
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')

def startVirtualMachineSoft(esxiIP, esxiUsername, esxiPassword, vmName):
    logging.debug('获取虚拟机{}的VMX配置文件路径'.format(vmName))
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    if vmx:
        if zhPattern.findall(vmx):
            logger.error(r'不支持中文名称的虚拟机')
            exit(1)
        cmd = r'"{}" {}'.format(vmx, r'start soft')
        result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
        logger.debug(r'{} {}'.format(vmx.split('/')[-1],result.strip()))

def startVirtualMachineHard(esxiIP, esxiUsername, esxiPassword, vmName):
    logging.debug("打开虚拟机{}的电源".format(esxiIP))
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    logging.debug("vmx路径:{}".format(vmx))
    if vmx:
        if zhPattern.findall(vmx):
            logger.error(r'不支持中文名称的虚拟机')
            exit(1)
        cmd = r'"{}" {}'.format(vmx, r'start hard')
        logging.debug("执行命令行:{}".format(cmd))
        result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
        logging.debug("命令执行完毕。")
        logger.debug(r'{} {}'.format(vmx.split('/')[-1],result.strip()))
    else:
        logging.debug("无法找到虚拟机名称{}".format(vmName))

def stopVirtualMachineSoft(esxiIP, esxiUsername, esxiPassword, vmName):
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    if vmx:
        if zhPattern.findall(vmx):
            logger.error(r'不支持中文名称的虚拟机')
            exit(1)
        cmd = r'"{}" {}'.format(vmx, r'stop soft')
        result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
        logger.debug(r'{} {}'.format(vmx.split('/')[-1],result.strip()))

def stopVirtualMachineHard(esxiIP, esxiUsername, esxiPassword, vmName):
    logging.debug("关闭虚拟机{}的电源".format(esxiIP))
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    logging.debug("vmx路径:{}".format(vmx))
    if vmx:
        if zhPattern.findall(vmx):
            logger.error(r'不支持中文名称的虚拟机')
            exit(1)
        cmd = r'"{}" {}'.format(vmx, r'stop hard')
        logging.debug("执行命令行:{}".format(cmd))
        result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
        logging.debug("命令执行完毕。")
        logger.debug(r'{} {}'.format(vmx.split('/')[-1],result.strip()))
    else:
        logging.debug("无法找到虚拟机名称{}".format(vmName))

def getVirtualMachineList(esxiIP, esxiUsername, esxiPassword):
    result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, r'-l')
    result = result.split('\n')
    i = 0
    for vmx in result:
        if vmx == '':
           result.pop(i)
        i = i + 1
    return result   #返回结果是一个列表

def callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd):
    if os.path.exists(vSphereCLI):
        output = os.popen(r'"{}" -H {}  -U {} -P {} {} '.format(vSphereCLI,
                                                                esxiIP,
                                                                esxiUsername,
                                                                esxiPassword,
                                                                cmd))
        return output.read()
    else:
        logger.error(r'请检查vSphere CLI是否安装或路径{}是否正确'.format(vSphereCLI))
        sys.exit(1)

def getVmxByVirtualMachineName(ip, username, password, name):
    vmxNamePattern = re.compile(name)
    vmList = getVirtualMachineList(ip, username, password)
    if vmList ==[]:
        logging.error('请检查配置，是否是ESXi主机')
        return False
    else:
        for vmx in vmList:
            if vmxNamePattern.search(vmx):
                return vmx

