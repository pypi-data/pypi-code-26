#!/usr/bin/env python
# coding: utf-8
"""
UGE qsub submit array-job
"""
__author__ = "Riku Okajima<riku.okajima@gmail.com>"
__date__ = "2018-06-04"
import argparse
import pathlib
from typing import List
from qjam.q_util import (
    aquire_script_path,
    create_file,
    escape_string,
    exec_script,
    format_parameter
)


def create_script(path: str, command: List[str],
                  params: List[List[str]], targets: List[str]):
    script = ["#!/bin/bash"]
    for p in params:
        script.append(format_parameter(p))

    script.extend([
        "",
        "seq_libs=(targets {})".format(" ".join(targets)),
        "seq_lib=${seq_libs[${SGE_TASK_ID}]}",
        "",
        ""
    ])

    for m in command:
        script.append(escape_string(m.replace("${}", "${seq_lib}")))
    create_file(path, script)


def manage_targets(targets: List[str], max_job_num: int=75000)\
        -> List[List[str]]:
    num = len(targets)
    target_list = []
    for i in range(num//75000+1):
        target_list.append(targets[i*max_job_num:(i+1)*max_job_num])
    return target_list


def gather_targets(glob: str, directory: str) -> List[str]:
    targets = []
    directory = pathlib.Path(directory)
    for f in directory.glob(glob):
        targets.append(escape_string(str(f)))
    return targets


def main(args: argparse.Namespace):
    """
    main function
    """
    targets = gather_targets(args.glob, args.dir)
    target_list = manage_targets(targets)

    if args.name is None:
        args.name = args.command[0].split(" ")[0].split("/")[-1]
    params = [
        ["-N", args.name],
        ["-S", args.shell],
        ["-o", args.output],
        ["-e", args.error],
        ["-l mem_user={mem}G -l h_vmem={mem}G -l mem_req={mem}G".format(
            mem=args.memory
        )]
    ]
    if args.cwd:
        params.append(["-cwd"])
    if not args.no_env:
        params.append(["-V"])
    if args.que is not None:
        params.append(["-q", args.que])
    if args.sync:
        params.append(["-sync", "y"])

    for target in target_list:
        params.append(["-t 1-{}:1".format(len(target))])

        path = aquire_script_path(args.path, args.name)
        create_script(path, args.command, params, target)
        exec_script(path)
