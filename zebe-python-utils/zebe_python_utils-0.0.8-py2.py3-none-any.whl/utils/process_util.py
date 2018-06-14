# -*- coding: utf-8 -*-
"""
    zebe.util.process_util
    ~~~~~~~~~~~~~~~~

    进程工具类

    :copyright: (c) 2018 by Zebe.
    :license: BSD, see LICENSE for more details.
"""

import os


def execute_cmd(cmd):
    """
    执行命令
    :param cmd: 命令内容
    :return:
    """
    f = os.popen(cmd)
    txt = f.readlines()
    return len(txt) > 0


def find_python_process_by_name(name):
    """
    查找指定名称的python进程
    :param name: 进程名称
    :return: 返回进程ID列表
    """
    pid_list = []
    cmd = "ps -ef| grep python"
    f = os.popen(cmd)
    txt = f.readlines()
    if len(txt) == 0:
        return False
    else:
        for line in txt:
            column_array = line.split()
            pid = column_array[1]
            for column in column_array:
                if str(column) == name:
                    pid_list.append(int(pid))
    return pid_list


def kill_python_process_by_name(name):
    """
    杀死指定名称的python进程
    :param name: 进程名称
    :return: 如果成功杀死则返回 True，否则返回 False
    """
    pid_list = find_python_process_by_name(name)
    for i in range(len(pid_list)):
        cmd = "kill -9 %s" % str(pid_list[i])
        os.system(cmd)
    return len(find_python_process_by_name(name)) == 0

