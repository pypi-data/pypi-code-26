#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analyzer import Analyzer
from argparse import ArgumentParser
from logger import logger
from monitor import Monitor

def main():
    parser = ArgumentParser(description='This is a link analysis tool that can customize keywords and output excel')
    parser.add_argument('--mode', default='auto', type=str, help='link analyze mode, auto or sauto')
    parser.add_argument('--automodefile', default='', type=str, help='choose param file in auto mode, '
                                                                     'include browser path and urls')
    parser.add_argument('--keywords', default=[], nargs='+', help='output the link which keywords in')
    parser.add_argument('--nokeywords', default=[], nargs='+', help='output the link which nokeywords no in')
    parser.add_argument('--extractkeys', default=[], nargs='+', help='extract keys to excel column')

    args = parser.parse_args()
    logger("param: " + str(args))
    try:
        if args.mode == "auto":
            logger('start auto analyzer')
            analyzer = Analyzer(args.keywords, args.nokeywords, args.extractkeys)
            analyzer.start(args.automodefile)
            logger('finish auto analyzer')
        elif args.mode == "sauto":
            logger('start manual analyzer')
            monitor = Monitor(args.keywords, args.nokeywords, args.extractkeys)
            monitor.start()
            logger('finish manual analyzer')
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    main()
    logger('finish main')
