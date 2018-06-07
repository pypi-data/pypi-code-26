#!python
"""Python script for BOUT++ job submission on **NERSC**. """

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

__author__ = 'Jianguo Chen'
__email__ = 'cjgls@pku.edu.cn'
__version__ = '2.1.1'
__date__ = '10/03/2017'

import argparse
import os
import sys
import glob
import numpy as np
from subprocess import check_output

from boutpy.boututils.functions import get_yesno

parser = argparse.ArgumentParser(
    description="Python script for BOUT++ Job submission on NERSC")
# formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '-a', '--afterany', nargs='?', type=int,
    help='defer job after the job `AFTERANY` finished')
parser.add_argument(
    '-c', '--cpus_per_task', type=int, default=None,
    help='run *cpus* threads per MPI task '
         '[default: 2(edison), 2(cori), 4(knl)]')
parser.add_argument(
    '--cpu_bind', nargs='?', default='cores',
    help=' [default: cores]')
parser.add_argument(
    '-d', '--data', action='store_true',
    help='the path is data_path [default: False]')
parser.add_argument(
    '-e', '--exe', nargs='?', default=None,
    help='executable file name')
parser.add_argument(
    '-i', '--info', action='store_true',
    help='Print more informations [default: False]')
parser.add_argument(
    '-l', '--label', nargs='?', default=None,
    help='label for job')
parser.add_argument(
    '-L', '--License', nargs='?', default='SCRATCH',
    help='specify the file system needed for jobs')
parser.add_argument(
    '-m', '--job-num-max', type=int, default=1,
    help='run this job for `job_num_max` times')
parser.add_argument(
    '--mode', nargs='?', default='quad,cache',
    help='KNL processor modes [default: quad,cache]')
parser.add_argument(
    '-n', '--ntasks', type=int, default=512,
    help='specify the number of tasks to run')
parser.add_argument(
    '--ntasks-per-node', type=int, default=None,
    help='use ntasks per node '
         '[default: 24(edison), 32(cori), 64(knl)]')
parser.add_argument(
    '-N', '--nodes', type=int, default=None,
    help='number of nodes')
parser.add_argument(
    '-p', '--partition', choices=['debug', 'regular', 'd', 'r'],
    default='debug',
    help='specify the partition for the jobs [default: debug]')
parser.add_argument(
    'path', nargs='*', default=['./'],
    help='working directories [default: ./]')
parser.add_argument(
    '-r', '--restart', action='store_true',
    help='restart job [default: False]')
parser.add_argument(
    '-t', '--time', nargs='?', default='30:00',
    help='specify the maximum wallclock time for the jobs '
         '[default: 30:00]')

args = parser.parse_args()
if args.info:
    print(args)

args.path = [ipath for ipath in args.path
    if os.path.isdir(ipath) and
        (os.path.isfile(os.path.join(ipath, 'BOUT.inp')) or
         os.path.isfile(os.path.join(ipath, 'data/BOUT.inp')))]
if args.nodes and args.ntasks_per_node:
    args.ntasks = args.nodes * args.ntasks_per_node
elif args.ntasks_per_node:
    args.nodes = int(np.ceil(args.ntasks * 1.0 / args.ntasks_per_node))
elif args.nodes:
    args.ntasks_per_node = args.ntasks / args.nodes

# check server settings
server = os.environ['NERSC_HOST']
CPU_TARGET = os.environ['CRAY_CPU_TARGET']
additions = []  # additional SBATCH options

# TODO: check setting of ntasks, cpus
if CPU_TARGET == 'sandybridge':
    print("On Edison/NERSC:")
    if (not args.ntasks_per_node) or (args.ntasks_per_node > 24):
        args.ntasks_per_node = 24
        args.nodes = int(np.ceil(args.ntasks * 1.0 / args.ntasks_per_node))
    if not args.cpus_per_task:
        args.cpus_per_task = 2
elif CPU_TARGET == 'haswell':
    print("On CORI-hsw/NERSC:")
    additions.append("#SBATCH -C haswell")
    if (not args.ntasks_per_node) or (args.ntasks_per_node > 32):
        args.ntasks_per_node = 32   # total 32
        args.nodes = int(np.ceil(
            args.ntasks * 1.0 / args.ntasks_per_node))
    if not args.cpus_per_task:
        args.cpus_per_task = 2
elif CPU_TARGET == 'mic-knl':
    print("On CORI-knl/NERSC:")
    additions.append("#SBATCH -C knl,{}".format(args.mode))
    if (not args.ntasks_per_node) or (args.ntasks_per_node > 64):
        args.ntasks_per_node = 64   # total 68
        args.nodes = int(np.ceil(
            args.ntasks * 1.0 / args.ntasks_per_node))
    if not args.cpus_per_task:
        args.cpus_per_task = 4
else:
    # general case
    print("WARNING: SERVER not recognized!!!")
    # TODO: using options to add additional control
    pass

# check partition setting
if args.partition in ['r', 'regular']:
    args.partition = 'regular'
elif args.partition in ['d', 'debug']:
    args.partition = 'debug'
else:
    print("WARNING: unrecognized partition")
    print("         set to 'debug'")
    args.partition = 'debug'


jobscript = """#!/bin/bash
#SBATCH -p {partition}
#SBATCH -N {nodes}
#SBATCH -t {time}
#SBATCH -J {jobname}
#SBATCH -L {License}
#SBATCH -o {outfile}
#SBATCH -D {workdir}
{additions}

#OpenMP settings:
export OMP_NUM_THREADS={cpus_per_task}
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

restart={restart}
job_num_max={job_num_max}
# set 'job_number' to be submiting times if it is undefined
: ${{job_number:=${{restart}}}}
job_num_max=$(( job_num_max+restart ))

echo $(date)
echo -e "exe_file:\\n  {exefile}"
echo -e "data_path:\\n  {data_path}"
# script file
script={script_path}

if [[ ${{job_number}} -lt ${{job_num_max}} ]]
then
    echo "hi from #$((job_number-restart+1)) job: ${{SLURM_JOB_ID}}"
    echo -e "  walltime = {time}"
    echo -e "  job_num_max = $((job_num_max-restart))"

    if [[ ${{job_num_max}} -gt 1 ]]
    then
        # change job name
        sed -i "0,/-J/{{s/-J [0-9_]*_/-J \
$((job_number+1))_$((job_num_max-restart))_/}}" ${{script}}
        # change output filename
        sed -i "0,/-o/{{s/[0-9_]*out$/$((job_number+1))_\
$((job_num_max-restart))_out/}}" ${{script}}
    fi

    # submit next job
    next_job_num=$(( job_number+1 ))
    if [[ ${{next_job_num}} -lt ${{job_num_max}} ]]
    then
        next_jobid=$(sbatch --export=job_number=${{next_job_num}} \
-d afterany:${{SLURM_JOB_ID}} $script)
        echo -e "  submitted #${{next_job_num}} job: ${{next_jobid}}"
    fi

    # run job
    echo -e "  running #$((job_number-restart+1)) job: ${{SLURM_JOB_ID}}..."
    if [[ ${{job_number}} -eq 0 ]]
    then
        {command}
    else
        echo "  restart = True"
        {command} restart append
    fi
    # end of the job

    (( job_number++ ))
fi
"""
command = ("srun -n {ntasks} -c {cpus_per_task} {cpu_bind} "
           "{exe} {data_path}")

dict_command = {
    'ntasks': args.ntasks,
    'cpus_per_task': args.cpus_per_task,
    'cpu_bind': ('--cpu_bind=' + args.cpu_bind
                 if server == 'cori' else ""),
    # set in the loop
    'exe': "[./exe]",
    'data_path': "[-d data_path]" if args.data else ""}

dict_opts = {
    'partition': args.partition,
    'nodes': args.nodes,
    'time': args.time,
    'License': args.License,
    'jobname': "[jobname]",             # set in the loop
    'outfile': "[outfile]",             # set in the loop
    'exefile': "[exefile]",             # set in the loop
    'workdir': "[exe_path]",            # workdir = exe_path
    'data_path': "[data_path]",         # set in the loop
    'additions': "\n".join(additions),  # set in the loop
    'restart': 1 if args.restart else 0,
    'script_path': "[script_path]",
    'job_num_max': args.job_num_max,
    'command': command.format(**dict_command),
    'cpus_per_task': args.cpus_per_task,
    }

exe = None
# flag1: check executable file in current path
if args.data:
    cxx = glob.glob("*.cxx")
    if not args.exe and len(cxx) == 1:
        exe = os.path.splitext(cxx[0])[0]
    elif not args.exe:
        print("ERROR: Failed to detect executable file!!!")
        if len(cxx) > 1:
            print("       multi cxx source files detected!!!")
        print("       using option `-e` to specify the file!!!")
        sys.exit(1)
    elif args.exe:
        exe = args.exe

    if not (os.path.isfile(exe) and
            os.access(exe, os.X_OK)):
        print("ERROR: No executable file exists in current path!!!")
        sys.exit(1)
    exe = os.path.realpath(exe)

if args.info:
    print("-" * 15 + " Jobscript template " + "-" * 15)
    print(jobscript.format(**dict_opts))
    print("-" * 50)
print("{:>14s}: {}".format("partition", args.partition))
print("{:>14s}: {}".format("MPI tasks", args.ntasks))
print("{:>14s}: {}".format("nodes", args.nodes))
print("{:>14s}: {}".format("Walltime", args.time))
print("{:>14s}: {}".format("times", args.job_num_max))
print("{:>14s}: {}".format("restart", args.restart))
print("{:>14s}: {}".format("datapath?", args.data))
print("{:>14s}: {}".format("path", args.path))
if args.afterany:
    print("{:>14s}: {}".format("dependency", args.afterany))
if exe:
    print("{:>14s}: {}".format("exe", exe))
if args.label:
    print("{:>14s}: {}".format("label", args.label))

if additions:
    print("-" * 15 + " additions " + "-" * 15)
    print("\n".join(additions))
    print("-" * 15 + " additions " + "-" * 15)

if not args.restart:
    args.label = "0_" + args.label if args.label else "0"
    # print("\nWARNING:\n    data will be covered if they exist!!!\n")
    suffix = '_%j.out'
else:
    args.label = "1_" + args.label if args.label else "1"
    suffix = '_%j.1out'

ok = raw_input('OK?[Y]/n: ') or 'Y'
if ok not in ['Y', 'y', 'YES', 'yes', 'Yes']:
    print("DO NOTHING!!!!")
    sys.exit(0)

print("Submitting jobs ...")
if exe:
    exe_path = os.path.dirname(os.path.realpath(exe))
    exe = os.path.basename(exe)
    exefile = os.path.join(exe_path, exe)

success = []
for ipath in args.path:
    idir = os.path.realpath(ipath)
    identity = idir.split('/')[-1]
    if args.job_num_max == 1:
        filename_script = 'bout.sbatch'
    else:
        filename_script = identity + '.sbatch'
    if not os.path.isdir(idir):
        continue

    # check executable file
    if args.data:
        # executable detected in `flag1`
        data_path = os.path.realpath(idir)
        idir = os.path.dirname(data_path)
    else:
        data_path = os.path.join(idir, 'data')
        cxx = glob.glob(os.path.join(idir, "*.cxx"))
        if (not args.exe) and len(cxx) == 1:
            exe = os.path.splitext(cxx[0])[0]
            exe_path = os.path.dirname(os.path.realpath(exe))
            exe = os.path.basename(exe)
            exefile = os.path.join(exe_path, exe)
            if not (os.path.isfile(exefile) and os.access(exefile, os.X_OK)):
                print("ERROR: No executable file exists!!!")
                sys.exit(1)
        else:
            print("ERROR: Failed to detect executable file!!!")
            if len(cxx) > 1:
                print("       multi cxx source files detected!!!")
            print("       using option `-e` to specify the exe file!!!")
            sys.exit(1)

        print("data_path: ", data_path)
        print("cxx: ", cxx[0])
        print("exe: ", exe)

    dict_opts['jobname'] = (args.label + '_' + identity
                            if args.label else identity)
    dict_opts['additions'] = '\n'.join(additions)
    dict_opts['outfile'] = os.path.realpath(
        os.path.join(idir, identity)) + suffix
    dict_opts['exefile'] = exefile
    dict_opts['workdir'] = exe_path
    dict_opts['data_path'] = data_path

    # set data path
    if args.data:
        dict_command['data_path'] = (
            '-d ' + os.path.realpath(data_path))

    tmp_dmp = os.path.join(data_path, 'BOUT.dmp.0.nc')
    if (not args.restart) and os.path.exists(tmp_dmp):
        print("WARNING: data already exist in\n    {}".format(tmp_dmp))
        if not get_yesno("Overwrite?", default=False):
            continue
    dict_command['exe'] = './' + exe
    dict_opts['command'] = command.format(**dict_command)
    script_path = os.path.join(idir, filename_script)
    dict_opts['script_path'] = script_path
    # output to `filename_script`
    with open(script_path, 'w') as output:
        output.write(jobscript.format(**dict_opts))

    if args.afterany:
        dependence = " -d afterany:{}".format(args.afterany)
    else:
        dependence = ""
    try:
        stdout = check_output("sbatch {} {}".format(
                              dependence, script_path), shell=True)
        print("  {}\t: {}".format(identity, stdout))
    except:
        break
    success.append(identity)

if success:
    print("Successfully submit jobs:\n    ", success)
