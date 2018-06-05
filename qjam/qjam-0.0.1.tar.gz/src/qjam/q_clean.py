#!/usr/bin/env python
# coding: utf-8
"""
remove qsub script & log files
"""
__author__ = "Riku Okajima<riku.okajima@gmail.com>"
__date__ = "2018-05-31"

import argparse
import pathlib


def main(args: argparse.Namespace):
    """
    main function
    """
    # TODO: add check when not force option
    qsub = pathlib.Path(args.path)
    output = pathlib.Path(args.output)
    error = pathlib.Path(args.error)
    for i in qsub.iterdir():
        if "_".join(i.name.split("_")[:-2]) == args.job:
            i.unlink()
    for i in output.iterdir():
        if i.name.split(".")[0] == args.job:
            i.unlink()
    for i in error.iterdir():
        if i.name.split(".")[0] == args.job:
            i.unlink()
