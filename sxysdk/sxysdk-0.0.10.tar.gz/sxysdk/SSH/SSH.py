# -*- coding: utf-8 -*-
import os
import logging
import paramiko
import socket

logger = logging.getLogger('root.InfoCoreTools.SSH')

#测试免密登录
#按照windows bat脚本提示，最终看到日期打印即为成功
def verifySSH(sshPath):
    if os.path.exists(sshPath):
        os.system(r'start {}\SSHBat\ssh.bat "{}"'.format(os.path.dirname(__file__), sshPath))

def verifySSH1(ip, username, sshPath):
    if os.path.exists(sshPath):
        output = os.popen(r'"{}" {}@{} date'.format(sshPath, username, ip))

def disableFCSwitchPort(switchIP, portNumber, sshPath):
    username = r'admin'
    if os.path.exists(sshPath):
        os.popen(r'"{}" {}@{} portdisable {}'.format(sshPath, username, switchIP, portNumber))

def enableFCSwitchPort(switchIP, portNumber, sshPath):
    username = r'admin'
    if os.path.exists(sshPath):
        os.popen(r'"{}" {}@{} portenable {}'.format(sshPath, username, switchIP, portNumber))

def linuxShutDownRemoteMachine(ip,username,password):
    port = 22
    cmd = r'poweroff'
    ssh(ip, port, username, password, cmd)

def linuxRebootRemoteMachine(ip,username,password):
    port = 22
    cmd = r'reboot'
    ssh(ip, port, username, password, cmd)

def ssh(ip,port,username,password,cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip,port,username,password)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        ssh.close()
        return output,True
    except socket.gaierror as e:
        logging.error('IP地址非法。错误信息：{}'.format(e))
        ssh.close()
        return 'ip_error',False
    except TimeoutError as e:
        logging.error('连接超时，可能是由于IP地址或端口不正确。错误信息:{}'.format(e))
        ssh.close()
        return 'timeout_error',False
    except paramiko.ssh_exception.AuthenticationException as e:
        logging.error('认证失败，用户名或密码不正确。错误信息{}'.format(e))
        ssh.close()
        return 'auth_failed_error',False
    except paramiko.ssh_exception.NoValidConnectionsError as e:
        logging.error('错误信息{}'.format(e))
        ssh.close()
        return 'port_error',False
    except Exception as e:
        logging.exception('未知错误 {}'.format(e))
        ssh.close()
        return 'other_error',False
