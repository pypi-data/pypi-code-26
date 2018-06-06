#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analyzer import Analyzer
from argparse import ArgumentParser
from logger import logger
from httprequestsniffer import HttpRequestSniffer

def main():
    parser = ArgumentParser()
    parser.add_argument('--automodefile', default='', type=str)
    parser.add_argument('--mode', default='auto', type=str)
    parser.add_argument('--keywords', nargs='+')

    args = parser.parse_args()
    logger("param: " + str(args))
    try:
        if args.mode == "auto":
            logger('start Analyzer')
            analyzer = Analyzer()
            analyzer.analyze(args.automodefile)
            logger('finish Analyzer')
        elif args.mode == "manual":
            logger('start HttpRequestSniffer')
            httpRequestSniffer = HttpRequestSniffer(keywords=args.keywords)
            httpRequestSniffer.start()
            logger('finish HttpRequestSniffer')
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    main()
