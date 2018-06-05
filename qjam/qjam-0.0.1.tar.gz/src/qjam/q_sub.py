#!/usr/bin/env python
# coding: utf-8
"""
UGE qsub wrapper
"""
__author__ = "Riku Okajima<riku.okajima@gmail.com>"
__date__ = "2018-06-04"
import argparse
from typing import List
from qjam.q_util import (
    aquire_script_path,
    create_file,
    escape_string,
    exec_script,
    format_parameter
)


def create_script(path: str, command: List[str], params: List[List[str]]):
    script = ["#!/bin/bash"]
    for p in params:
        script.append(format_parameter(p))
    script.extend(["", ""])
    for m in command:
        script.append(escape_string(m))
    create_file(path, script)


def main(args: argparse.Namespace):
    """
    main function
    """
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

    path = aquire_script_path(args.path, args.name)
    create_script(path, args.command, params)
    exec_script(path)
