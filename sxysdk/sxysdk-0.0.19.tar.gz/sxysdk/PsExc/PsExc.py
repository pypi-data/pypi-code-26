# -*- coding: utf-8 -*-

#PsExec是一个轻型的 telnet 替代工具，它使您无需手动安装客户端软件即可执行其他系统上的进程，并且可以获得与控制台应用程序相当的完全交互性。
#PsExec最强大的功能之一是在远程系统和远程支持工具中启动交互式命令提示窗口，以便显示无法通过其他方式显示的有关远程系统的信息。
#注意这个exe在调用前，先用cmd命令行打开运行打开一下，它会有一个询问对话框，需要第一次确认一下。

import os


import logging
logger = logging.getLogger('sxysdk.PsExc')

father = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
psexec64 = r'{}\Tools\PSTools\PsExec64.exe'.format(father)
psexec32 = r'{}\Tools\PSTools\PsExec.exe'.format(father)
bang = r'{}\Tools\TestTools\osrbang.exe'.format(father)


def doRemoteWinCmd(ip, username, password, cmd, interactive_mode=False, full_result=False, arch=64):
    """远程执行Windows命令

    :param ip: 远程计算机IP
    :param username: 远程计算机用户名
    :param password: 远程计算机密码
    :param cmd: 执行的cmd命令
    :param interactive_mode: 是否交互模式
    :param full_result: 是否完全返回打印信息
    :param arch: 调用工具版本（32位还是64位，默认64位）
    :return: 返回字符串，内容为打印信息
    """

    try:
        if arch == 32:
            psexec = psexec32
        else:
            psexec = psexec64

        if not os.path.exists(psexec):
            raise FileNotFoundError(psexec)

        if interactive_mode == True:
            interactive = '-i'
        else:
            interactive = ''

        do_cmd = r'"{}" -s \\{} -u {} -p "{}" {} cmd.exe /c "{}" 2>&1'.format(psexec, ip, username, password, interactive, cmd)
        logging.debug('执行命令行:{}'.format(do_cmd))
        rs = os.popen(do_cmd).read()

        if rs.find("版本不兼容") != -1:
            raise WindowsError('Psexec版本不兼容')

        rs = rs.split('\n')
        i = 0
        while 1:
            try:
                if rs[i] == '':  # 列表中删除所有的''元素
                    rs.pop(i)
                else:
                    i = i + 1
            except IndexError:
                break
        logging.debug('命令行执行结果:{}'.format(rs))

        if rs[-1].find('error code 0') != -1:
            rt = True
        else:
            rt = False

        if full_result == False:
            rs = rs[3]
        else:
            rs = rs
        return rt, rs
    except BaseException:
        raise OSError


#远程重启，用PsExec远程调用系统本地CMD命令（shutdown -r -t 0）实现
def winRebootRemoteMachine(ip, username, password, arch):
    logging.debug("重启计算机:{}".format(ip))
    cmd = r"shutdown -r -t 0 2>nul"
    doRemoteWinCmd(ip, username, password, cmd, arch=arch)


#远程正常关机，用PsExec64.exe远程调用系统本地CMD命令（shutdown -s -t 0）实现
def winShutdownRemoteMachine(ip, username, password, arch):
    logging.debug("关闭计算机:{}".format(ip))
    cmd = r"shutdown -s -t 0 2>nul"
    doRemoteWinCmd(ip, username, password, cmd, arch=arch)


def winBangRemoteMachine(ip, username, password, arch):
    logging.debug("bang计算机:{}".format(ip))
    cmd = r"{} -s >nul 2>nul".format(bang)
    doRemoteWinCmd(ip, username, password, cmd, arch=arch)


'''
def enableRemoteNetworkAdapter(ip, username, password, adapterName):
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c netsh interface set interface ""{}"" enabled 2>nul".format(psexec64,
                                                                                                         ip,
                                                                                                         username,
                                                                                                         password,
                                                                                                         adapterName)
    os.popen(cmd)

def disableRemoteNetworkAdapter(ip, username, password, adapterName):
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c netsh interface set interface ""{}"" disabled 2>nul".format(psexec64,
                                                                                                          ip,
                                                                                                          username,
                                                                                                          password,
                                                                                                          adapterName)
    os.popen(cmd)

def startRemoteMachineService(ip, username, password, serviceName):
    logging.debug('启动{}的{}服务'.format(ip,serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc start ""{}"" 2>nul".format(psexec64,
                                                                            ip,
                                                                            username,
                                                                            password,
                                                                            serviceName)
    os.popen(cmd)

def stopRemoteMachineService(ip, username, password, serviceName):
    logging.debug('停止{}的{}服务'.format(ip, serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc stop ""{}"" 2>nul".format(psexec64,
                                                                           ip,
                                                                           username,
                                                                           password,
                                                                           serviceName)
    os.popen(cmd)

def chkconfigRemoteMachineServiceOn(ip, username, password, serviceName):
    logging.debug('设置{}的{}服务为开机自动启动'.format(ip, serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc config ""{}"" start=auto 2>nul".format(psexec64,
                                                                                        ip,
                                                                                        username,
                                                                                        password,
                                                                                        serviceName)
    os.popen(cmd)

def chkconfigRemoteMachineServiceOff(ip, username, password, serviceName):
    logging.debug('设置{}的{}服务为开机手动启动'.format(ip, serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    cmd = r"{} -d \\{} -u {} -p {} cmd.exe /c sc config ""{}"" start=demand 2>nul".format(psexec64,
                                                                                          ip,
                                                                                          username,
                                                                                          password,
                                                                                          serviceName)
    os.popen(cmd)

def queryRemoteService(ip, username, password, serviceName):
    logging.debug('查询{}的{}的状态'.format(ip,serviceName))
    if os.path.exists(psexec64) == False:
        sys.exit(1)
    state = 'UNKNOW'
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c sc queryex ""{}"" 2>nul" .format(psexec64,
                                                                            ip,
                                                                            username,
                                                                            password,
                                                                            serviceName)
    result = os.popen(cmd)
    output = result.read().split('\n')
    for line in output:
        line = line.split()
        if len(line)!=0 and line[0] == 'STATE' and line[3] == 'RUNNING':
            return 'RUNNING'
        if len(line)!=0 and line[0] == 'STATE' and line[3] == 'STOPPED':
            return 'STOPPED'
    return state

def runRemoteMachineDisktest(ip, username, password):
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c start {} 2>nul".format(psexec64,ip,username,password,runDisktestBat)
    os.popen(cmd)

def runRemoteMachineDebugview(ip, username, password):
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c start {} 2>nul".format(psexec64, ip, username, password,startDebugviewBat)
    os.popen(cmd)

def deleteRemoteMachineSystemDump(ip, username, password):
    dumpFile = r'C:\Windows\MEMORY.DMP'.replace(r'C:', r'\\{}\c$'.format(ip))
    cmd = r"{} \\{} -u {} -p {} cmd.exe /c del {} 2>nul".format(psexec64, ip, username, password, dumpFile)
    os.popen(cmd)
'''