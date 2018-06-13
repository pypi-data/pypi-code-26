#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
FILE:
  cli.py

NAME:
  CLI - command line interface

DESCRIPTION:
  CLI entry

USAGE:
  $ python pipelane/cli.py <shell command>
  For example:
  $ python pipelane/cli.py echo 'Hello World'
  # Hello World

  After installation with pip `pip install pipelane`
  $ pipelane echo 'Hello World'
  # Hello World

'''

import sys
import subprocess

import notification.main as notification

def main():

  subprocess.call(sys.argv[1:])
  notification.send(' '.join(sys.argv[1:]), ''.join(sys.argv[:1]))


if __name__ == '__main__':
  main()