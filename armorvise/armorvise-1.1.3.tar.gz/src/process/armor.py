#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import re
import sys
import time
import subprocess
import shutil
import socket
import logging
from multiprocessing import Process
from libs.daemon import Daemon
from libs import util

_glob_pypath = sys.path[0]

class armor_missile(Daemon):
    def __init__(self, pidfile='/tmp/daemon.pid', stdin='/dev/null', stdout='/dev/null', stderr='/dev/null',input_data={}):
        super(armor_missile, self).__init__(pidfile,stdin,stdout,stderr,input_data)

    def run(self):
        sys.stdout.write("start,{};\n".format(os.getpid()))
        while 1:
            sys.stdout.write("Daemon Alive! {}\n".format(time.ctime()))

            ### 检查子进程
            if "cmd" in self.input_data:
                i_cmd = self.input_data["cmd"]
                sys.stdout.write("{}\n".format(i_cmd))

                check_pid,check_cmd,pro_cmd = util.get_proc(i_cmd)

                sys.stdout.write("check:{},{},{}\n".format(
                    check_pid,check_cmd,pro_cmd
                ))
                ### 不存在，那么创建一个
                if check_pid is None or check_cmd is None:
                    tmp_p = Process(target=util.exec_cmd,args=(i_cmd,self.now_path,))
                    tmp_p.start()
                    if tmp_p.is_alive():
                        sys.stdout.write('New-Process: %s is running\n' % tmp_p.pid)

            sys.stdout.flush()
            time.sleep(1)

if __name__ == '__main__':
    PIDFILE = '/tmp/daemon-armor.pid'
    LOG = '/tmp/daemon-armor.log'
    #p1 = Daemon(pidfile=PIDFILE, stdout=LOG, stderr=LOG)
    p1 = armor_missile(pidfile=PIDFILE, stdout=LOG, stderr=LOG ,input_data={
        "cmd":"cd {};sh test.sh>aa 2>&1".format(_glob_pypath)
    })
    p1.start()














