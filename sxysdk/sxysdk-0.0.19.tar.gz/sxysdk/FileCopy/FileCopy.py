# -*- coding:utf-8 -*-
import paramiko
import os
from subprocess import run

import logging
logger = logging.getLogger('sxysdk.FileCopy')

#注意：local_path必须是已经存在目录，如果目录不存在则抛异常FileNotFoundError
def download_file(ip, port, username, password, remote_file, local_path):
    file_name = os.path.basename(remote_file)
    local_file = '{}\{}'.format(local_path, file_name)
    t = paramiko.Transport((ip, port))
    t.connect(username=username, password=password)
    try:
        sftp = paramiko.SFTPClient.from_transport(t)
        logging.debug('拷贝文件->[{}][{}]'.format(ip,file_name))
        sftp.get(remotepath=remote_file, localpath=local_file)
        t.close()
        logging.debug('[{}][{}]文件拷贝完毕'.format(ip,file_name))
    except FileNotFoundError:
        logging.debug('{}没有{}日志文件'.format(ip,remote_file))
        t.close()
    except BaseException:
        logging.exception("未知错误")


def upload_file(ip, port, username, password, remote_path, local_file):
    file_name = os.path.basename(local_file)
    remote_file = '/{}/{}'.format(remote_path,file_name)
    t = paramiko.Transport((ip, port))
    t.connect(username=username, password=password)
    try:
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(localpath=local_file, remotepath=remote_file)
        t.close()
    except Exception as e:
        logging.exception("未知错误")
        t.close()


def win_download_file(ip, username, password, remote, local):
    logging.debug('连接管道 {}'.format(ip))
    logging.debug('拷贝文件->{}'.format(remote))
    run(r"net use \\{} {} /user:{} 2>nul 1>nul".format(ip, password, username),shell=True)
    remote = remote.replace(r'C:', r'\\{}\c$'.format(ip))
    run(r'xcopy "{}"  "{}" /y 2>nul 1>nul'.format(remote, local),shell=True)
    run(r"net use \\{} /d /y 1>nul".format(ip),shell=True)
    logging.debug('释放管道{}'.format(ip))


def win_download_dir(ip, username, password, dir, local):
    child_dir = os.path.split(dir)
    if child_dir[1] == '':  #目录的最后有/。
        child_dir = os.path.split(child_dir[0])
        remote = dir + '*.*'
    else:
        remote = dir + '/*.*'
    local = local + '/' + child_dir[1]
    os.makedirs(local)

    logging.debug('连接管道 {}'.format(ip))
    logging.debug('拷贝文件->{}'.format(remote))
    run(r"net use \\{} {} /user:{} 2>nul 1>nul".format(ip, password, username), shell=True)
    remote = remote.replace(r'C:', r'\\{}\c$'.format(ip))
    run(r'xcopy "{}"  "{}" /e 2>nul 1>nul'.format(remote, local), shell=True)
    run(r"net use \\{} /d /y 1>nul".format(ip), shell=True)
    logging.debug('释放管道{}'.format(ip))