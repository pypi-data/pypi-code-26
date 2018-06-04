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
import getopt
from armor import armor_missile
from libs import util
from libs import console
from libs import conf

def main(**kwargs):
    #options,args = getopt.getopt(sys.argv[1:],"hp:i:cb:",["help","ip=","port=","aaa"])
    # [('--help', '')] ['a', 'b', 'c']
    try:
        options,args = getopt.getopt(sys.argv[1:],conf.options_short,conf.options_long)
    except Exception,e:
        print console.help_out
        return

    if len(args) < 1 and len(options) < 1:
        print console.help_out
        return
        #raise RuntimeError("Param Not Enough!")

    if len(options) > 0:
        cons_obj = console.console_io(options)
        return

    cmd_part = args
    cmd_str = ' '.join(cmd_part)

    hash_str_pos,pro_cmd = util.md5_hash(cmd_str)

    PIDFILE = conf.conf_proc_pid_pre.format(hash_str_pos)
    LOG = conf.conf_proc_log_pre.format(hash_str_pos)

    p1 = armor_missile(pidfile=PIDFILE, stdout=LOG, stderr=LOG ,input_data={
        "cmd":cmd_str
    })
    p1.start()

if __name__ == '__main__':
    main()


