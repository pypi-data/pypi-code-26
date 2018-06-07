#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analyzer import Analyzer
from argparse import ArgumentParser
from logger import logger
from httprequestsniffer import HttpRequestSniffer
from monitor import Monitor
import json

def main():
    parser = ArgumentParser()
    parser.add_argument('--automodefile', default='', type=str)
    parser.add_argument('--mode', default='auto', type=str)
    parser.add_argument('--keywords', default=[], nargs='+')
    parser.add_argument('--nokeywords', default=[], nargs='+')
    parser.add_argument('--extractkeys', default=[], nargs='+')

    args = parser.parse_args()
    logger("param: " + str(args))
    try:
        if args.mode == "auto":
            logger('start auto analyzer')
            analyzer = Analyzer(args.keywords, args.nokeywords, args.extractkeys)
            analyzer.start(args.automodefile)
            logger('finish auto analyzer')
        elif args.mode == "manual":
            logger('start manual analyzer')
            monitor = Monitor(args.keywords, args.nokeywords, args.extractkeys)
            monitor.start()
            logger('finish manual analyzer')
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    main()
    logger('finish main')
