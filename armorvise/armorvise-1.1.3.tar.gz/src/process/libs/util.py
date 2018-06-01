#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
import re
import sys
import time
import hashlib
import subprocess
import shutil
import socket
import logging
import json
import signal
from conf import conf_proc_pid_fname,conf_pro_pid_end,conf_proc_root_dir
#sys.path.append("../ext")

MY_PATH = os.path.abspath(os.path.dirname(__file__))
EXT_PATH = "{}/../ext".format(MY_PATH)
INFO_JSON = "conf.json"
proj_info = json.loads(open(os.path.join(EXT_PATH, INFO_JSON)).read())

def r1(pattern, text): 
    m = re.search(pattern, text)
    if m:
        return m.group(1)

    return None

### 得到进程id和信息
def get_proc(name):
    global proj_info
    #name = re.sub(">.+","",name)
    for dirname in os.listdir('/proc'):
        if dirname == 'curproc':
            continue
     
        try:
            with open('/proc/{}/cmdline'.format(dirname), mode='rb') as fd:
                content = fd.read().decode().split('\x00')
                content_cmd = ' '.join(content)

                ### except process 'armorgo'
                if name in content_cmd and proj_info["name"] not in content_cmd:
                    return dirname,content_cmd,name
        except Exception:
            continue
     
        #for i in sys.argv[1:]:
            #if i in content[0]:
                #print('{0:<12} : {1}'.format(dirname, ' '.join(content)))

    return None,None,None

def get_all_proc():
    my_proc_arr = []

    for filename in os.listdir(conf_proc_root_dir):
        if conf_proc_pid_fname in filename and conf_pro_pid_end in filename:
            try:
                with open('{}{}'.format(conf_proc_root_dir,filename), mode='rb') as fd:
                    pid = r1("(\d+)",fd.read())

                    with open('/proc/{}/cmdline'.format(pid), mode='rb') as fd_info:
                        content = fd_info.read().decode().split('\x00')
                        content_cmd = ' '.join(content)

                        my_proc_arr.append({
                            "pid":pid,
                            "cmd":content_cmd
                        })
            except Exception,e:
                pass

    return my_proc_arr

def kill_all_proc():
    for filename in os.listdir(conf_proc_root_dir):
        if conf_proc_pid_fname in filename and conf_pro_pid_end in filename:
            try:
                with open('{}{}'.format(conf_proc_root_dir,filename), mode='rb') as fd:
                    pid = r1("(\d+)",fd.read())
                    print pid
                    print os.kill(int(pid), signal.SIGTERM)
            except Exception,e:
                print "error",e

def exec_cmd(cmd,exc_path):
    env = os.environ
    #if exc_path is not None:
        #cmd = "cd {}; {}".format(exc_path,cmd)
    try:
        p =	subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            #stdout=fhandle,
            #stderr=fhandle,
            shell=True,
            universal_newlines=True,
            env=env,
            cwd=exc_path
        ) 
        output, errout = p.communicate()
        sys.stdout.write("Exec Fin! {},{},{},{}\n".format(cmd,output,errout,exc_path))

    except Exception,e:
        sys.stdout.write("Exec Fail! {},{}\n".format(e,exc_path))

    sys.stdout.flush()

def md5_hash(strs):
    hl = hashlib.md5()
    hl.update(strs.encode(encoding='utf-8'))
    return hl.hexdigest(),strs

if __name__ == '__main__':
    print kill_all_proc()




