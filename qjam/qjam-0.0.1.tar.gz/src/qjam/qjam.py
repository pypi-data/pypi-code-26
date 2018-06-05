#!/usr/bin/env python
# coding: utf-8
"""
UGE qsub utility command
"""
__author__ = "Riku Okajima<riku.okajima@gmail.com>"
__date__ = "2018-05-31"

import argparse
from typing import List, Optional
from qjam import q_array, q_clean, q_sub


def get_args(argument: Optional[List[str]]=None) -> argparse.Namespace:
    """
    get arguments from command line
    """
    parser = argparse.ArgumentParser(description=__doc__, prog="qjam")
    # general arguments
    parser.add_argument(
        "-p", "--path",
        type=str,
        default="./qsub/",
        help="shellscript path"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./log/",
        help="specify standard output stream path(s)"
    )
    parser.add_argument(
        "-e", "--error",
        type=str,
        default="./log/",
        help="specify standard error stream path(s)"
    )

    subparsers = parser.add_subparsers(help="sub-command help")

    # submission arguments
    parser_sub = subparsers.add_parser(
        "sub",
        help="submit job"
    )
    parser_sub.set_defaults(func=q_sub.main)
    parser_sub.add_argument(
        "-c", "--command",
        nargs="+",
        type=str,
        default=None,
        help="command args"
    )
    parser_sub.add_argument(
        "-sync",
        action="store_true",
        help="wait job"
    )
    parser_sub.add_argument(
        "--no_env",
        action="store_true",
        help="send no variables"
    )
    parser_sub.add_argument(
        "-q", "--que",
        type=str,
        default=None,
        help="execution que"
    )
    parser_sub.add_argument(
        "-S", "--shell",
        type=str,
        default="/bin/bash",
        help="command interpreter to be used"
    )
    parser_sub.add_argument(
        "-cwd",
        type=bool,
        default=True,
        help="use current working directory"
    )
    parser_sub.add_argument(
        "-N", "--name",
        type=str,
        default=None,
        help="specify job name"
    )
    parser_sub.add_argument(
        "-l", "--memory",
        type=str,
        default="4",
        help="request the given memory"
    )

    # array arguments
    parser_array = subparsers.add_parser(
        "array",
        help="submit array-job"
    )
    parser_array.set_defaults(func=q_array.main)
    parser_array.add_argument(
        "glob",
        type=str,
        help="targets glob"
    )
    parser_array.add_argument(
        "--dir",
        type=str,
        default=".",
        help="target directory"
    )
    parser_array.add_argument(
        "-c", "--command",
        nargs="+",
        type=str,
        default=None,
        help="command args"
    )
    parser_array.add_argument(
        "-sync",
        action="store_true",
        help="wait job"
    )
    parser_array.add_argument(
        "--no_env",
        action="store_true",
        help="send no variables"
    )
    parser_array.add_argument(
        "-q", "--que",
        type=str,
        default=None,
        help="execution que"
    )
    parser_array.add_argument(
        "-S", "--shell",
        type=str,
        default="/bin/bash",
        help="command interpreter to be used"
    )
    parser_array.add_argument(
        "-cwd",
        type=bool,
        default=True,
        help="use current working directory"
    )
    parser_array.add_argument(
        "-N", "--name",
        type=str,
        default=None,
        help="specify job name"
    )
    parser_array.add_argument(
        "-l", "--memory",
        type=str,
        default="4",
        help="request the given memory"
    )

    # remove arguments
    parser_rm = subparsers.add_parser(
        "clean",
        help="remove qsub scripts & log files"
    )
    parser_rm.add_argument(
        "job",
        type=str,
        help="job name"
    )
    parser_rm.add_argument(
        "-f", "--force",
        action="store_true",
        help="remove files without check"
    )
    parser_rm.set_defaults(func=q_clean.main)

    args = parser.parse_args()
    return args, parser


def main():
    """
    main function
    """
    args, parser = get_args()
    if "func" in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
