#!/usr/bin/env python
"""
This script is for:
    - check job state including time info
    - cancel jobs (scancel)
    - update jobs (scontrol)

REQUIREMENTS:
    o slurm system with output filename: %j.out, i.e. JOBID.out
    o linux command: awk, grep, tail
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__author__ = 'Jianguo Chen'
__email__ = 'cjgls@pku.edu.cn'
__version__ = '2.0.1'
__date__ = '09/11/2017'

from builtins import input
from subprocess import check_output, check_call
import argparse
import sys
import os
from netCDF4 import Dataset
import re

parser = argparse.ArgumentParser(
    description='Check or modify jobs state',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-d', '--delete', action='store_true',
                    help='Delete jobs in queue')
parser.add_argument('-u', '--update', action='store_true',
                    help='Modify jobs state')

args = parser.parse_args()

# get job information
# %i ID %P partition %j jobname %t state %D number of nodes
# %M time used %l timelimit %Z workdir
jobinfo = check_output('squeue -u $USER -o "%i %P %j %t %D %M %l %Z"',
                       shell=True, universal_newlines=True).split('\n')

# remove empty string
jobinfo = list(filter(None, jobinfo))

jobinfo = [jobinfo[i].split() for i in range(len(jobinfo))]
# sorted by job state and jobid
jobinfo[1:] = sorted(jobinfo[1:], key=lambda x: (x[3], -int(x[0])),
                     reverse=True)

# print title without workdir
formatter = ("{n:>2s} {0:8s}{1:10s}{2:21.20s}"
             + "{3:3s}{4:6s}{5:9s}{6:11s}{t:7s}")
# {:21.20s} give the precision of str,
# i.e. auto truncate the string if string is too long
print(formatter.format(*jobinfo[0][:-1], n='NO', t='T_ARRAY'))

printonce = 1     # print a blank line only once

for i in range(1, len(jobinfo)):
    if not (jobinfo[i][3] == 'R') and printonce:   # JOBSTATE: RUNNING
        if i == 1:
            printonce = 0
        else:
            print('----------')
            printonce = 0

    # get t_array[-1]
    t_array = 'N/A'
    try:
        stdout = check_output("scontrol show jobid {} | grep StdOut |\
            awk -F= '{{print $2}}'".format(jobinfo[i][0]),
            shell=True, universal_newlines=True)
        stdout = stdout[:-1]    # drop '\n'
        if not os.path.isfile(stdout):
            raise ValueError
        try:
            pattern = 'Reading options file '
            DataDir = check_output(
                "grep '{}' {} | awk -F'{}' '{{print $2}}'"
                .format(pattern, stdout, pattern),
                shell=True, universal_newlines=True)
            DataDir = os.path.dirname(DataDir)
        except:
            raise

        dmp = Dataset(os.path.join(jobinfo[i][-1], DataDir, 'BOUT.dmp.0.nc'))
        t_array = str(dmp.variables['t_array'][-1])
        dmp.close()
    except:
        t_array = 'N/A'

    """
    # get all stdout file and sort by time
    stdout = sorted(glob.glob("{}/*.out".format(jobinfo[i][-1])),
                    key=getmtime, reverse=True)
    for istdout in stdout:
        if isfile(istdout):
            # get last timestep
            stepinfo = check_output(
                "awk '/wall_limit/, O' {} | grep 'e+' | tail -n1".
                format(istdout),
                shell=True, universal_newlines=True).split()
            if len(stepinfo):
                t_array=[ t for t in stepinfo if 'e+' in t]
                t_array=str(float(t_array[0]))
                break
    else:
        t_array='N/A'
    """

    print(formatter.format(*jobinfo[i][:-1], n=str(i), t=t_array))

short = '    {n:>2s}  {name:21.20s}{jobid:8}'
# delete jobs
serial_no = set()
if args.delete:
    str_num = input('\ndelete jobs: ')
    # input e.g.: 1,2 ; 4:5
    str_num = re.split(';|,', str_num)  # split by ';' or ','
    str_num = list(filter(None, str_num))
    try:
        for i in str_num:
            if ':' in i:
                tmp = [int(ii) for ii in i.split(':')]
                serial_no = serial_no.union(
                    set(range(tmp[0], tmp[1] + 1)))
            else:
                serial_no.add(int(i))
    except ValueError:
        print("\nERROR: The delimiter should be ',' or ';'\n")
        sys.exit()
    # ensure serial_no in jobs size
    serial_no.intersection_update(set(range(1, len(jobinfo))))
    if not serial_no:
        sys.exit()

    print(short.format(n='NO', name='NAME', jobid='JOBID'))
    for i in serial_no:
        print(short.format(n=str(i), name=jobinfo[i][2],
                           jobid=jobinfo[i][0]))

    sure = input("\nSure?[y/N] : ") or 'N'
    if sure in ['y', 'Y', 'yes', 'YES', 'Yes']:
        print("\ndeleting ...")
        for i in serial_no:
            check_call('scancel ' + jobinfo[i][0], shell=True)

        print
        check_call(sys.argv[0])
    else:
        print("DO NOTHING!")

# update jobs queue
if args.update:
    str_num = input('\nupdate jobs: ')
    # input e.g.: 1,2 ; 4:5
    import re
    str_num = re.split(';|,', str_num)  # split by ';' or ','
    str_num = list(filter(None, str_num))
    try:
        for i in str_num:
            if ':' in i:
                tmp = [int(ii) for ii in i.split(':')]
                serial_no = serial_no.union(
                    set(range(tmp[0], tmp[1] + 1)))
            else:
                serial_no.add(int(i))
    except ValueError:
        print("\nERROR: The delimiter should be ',' or ';'\n")
        sys.exit()
    # ensure serial_no in jobs size
    serial_no.intersection_update(set(range(1, len(jobinfo))))
    if not serial_no:
        sys.exit()

    print(short.format(n='NO', name='NAME', jobid='JOBID'))
    for i in serial_no:
        print(short.format(n=str(i), name=jobinfo[i][2],
                           jobid=jobinfo[i][0]))

    sure = input("\nSure?[y/N] : ") or 'N'
    if sure in ['y', 'Y', 'yes', 'YES', 'Yes']:
        update_conf = input(
            'Update configuration [partition, Timelimit ...]:\n\t')
        # update configuration: partition=debug Timelimit=30:00

        for i in serial_no:
            # can set `update to other command
            try:
                command = 'scontrol update jobid={} {}'.format(
                    jobinfo[i][0], update_conf)
                check_call(command, shell=True)
            except Exception as ex:
                print(ex)
                print("ERROR: can not update job state: \n\t")
                print(i, jobinfo[i][2])
                # sys.exit()
        print
        check_call(sys.argv[0])
    else:
        print("DO NOTHING!")
