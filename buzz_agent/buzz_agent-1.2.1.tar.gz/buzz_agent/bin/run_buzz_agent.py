#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import imp
import buzz_agent
from buzz_agent import BuzzAgent


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='config file', action='store', required=True)
    parser.add_argument('-v', '--version', action='version', version='%s' % buzz_agent.__version__)

    return parser


def load_config(filename):
    d = imp.new_module('config')
    d.__file__ = filename
    try:
        with open(filename) as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
    except IOError as e:
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return d


def main():
    args = build_parser().parse_args()

    agent = BuzzAgent(config=load_config(args.config))

    agent.run()

if __name__ == '__main__':
    main()
