import os
from easilyb.commands import get_command_output, run_command

import logging
logger = logging.getLogger(__name__)

_PS_TO_INT = ['PID', 'PPID', 'RSS']



def meminfo():
    total, free= 0,0
    with open('/proc/meminfo') as fin:
        for line in fin.readlines():
            sline = line.split()
            if str(sline[0]) == 'MemTotal:':
                total = int(sline[1])
            elif str(sline[0]) == 'MemFree:':
                free = int(sline[1])
    return total, free




def get_processes():
    output, err = get_command_output(['ps', '-Ao', 'pid,ppid,uname,rss,comm=PROG,command=CMDLINE'])
    lines = output.split('\n')
    header = lines[0].split()
    processes = [line.split(None, len(header) - 1) for line in lines[1:] if len(line)>0]
    processes2 = list()
    for processe in processes:
        processes2.append({header[j]: (int(processe[j]) if header[j] in _PS_TO_INT else processe[j])for j in range(len(header))})
    return processes2

def get_process(pid, processes=None):
    if processes is None: processes = get_processes()
    for process in processes:
        if process['PID']==pid:
            return process
    return None

def get_process_children(pid=None, recursive=False, processes=None):
    childs = list()
    if pid is None:
        pid = os.getpid()
    if processes is None: processes = get_processes()
    for p in processes:
        if int(p['PPID']) == pid:
            childs.append(p)
            if recursive:
                childs.extend(get_process_children(pid=p['PPID'], recursive=False, processes=processes))
    return childs


def get_open_ports():
    return_code, output = run_command(["netstat", "-lnt"])
    ret = list()
    if return_code != 0:
        logging.error("netstat returned a non zero code: %d", return_code)
    else:
        lines = output.split('\n')
        for line in lines:
            if 'LISTEN' in line and not 'tcp6' in line:
                try:
                    parts = line.split()
                    host, port = parts[3].split(':')
                    port = int(port)
                    if not port in ret:
                        ret.append(port)
                except Exception as e:
                    logging.warn("exception parsing a line in netstat output: %s (line=%s)" % (str(e), line), exc_info=True)
    return ret