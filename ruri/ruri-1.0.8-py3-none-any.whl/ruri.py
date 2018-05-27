#!/usr/bin/env python3
# Released under the GPL license http://www.gnu.org/licenses/gpl-3.0.txt

import argparse
import logging
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
from .assistant import Assistant
from .crc32 import Crc32
from .vars import VERSION


def main():
    parser = argparse.ArgumentParser(description="Ruri")
    parser.add_argument("-r", "--recursive", help="work recursively", action="store_true")
    parser.add_argument("-t", "--threads", help="override the amount of threads", type=int, default=1)
    parser.add_argument("-v", "--verbose", help="output level", action="store_true")
    parser.add_argument("-q", "--quiet", help="Do not print progressbars.", action="store_true")
    parser.add_argument("--version", help="Print the version number, and exit.", action="version",
                        version="%(prog)s version " + VERSION)
    parser.add_argument("file", nargs='+', help="The file(s) you need CRC'ed")
    try:
        args = parser.parse_args()
    except:
        Assistant(False).print_end(8)

    assistant = Assistant(args.quiet)
    crc32 = Crc32(assistant)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s]\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    threads = args.threads
    assistant.logger.debug("Threads set at %s" % str(args.threads))

    if args.recursive:
        if not assistant.quiet_mode:
            assistant.logger.warning(
                "%s\t%s" % (
                    assistant.text_purple("WARNING"),
                    assistant.text_red("Experimental feature")
                )
            )
        assistant.logger.debug("len(args.file) = %s" % (len(args.file)))
        file_set = set()
        try:
            for root_dir in args.file:
                for root, dirs, files in os.walk(root_dir):
                    for file in files:
                        rel_dir = os.path.relpath(root, ".")
                        rel_file = os.path.join(rel_dir, file)
                        file_set.add(rel_file)
                pool = ThreadPool(threads)
                results = pool.map(crc32.crc32, file_set)
                pool.close()
            pool.join()
            assistant.logger.debug("results = %s" % results)
            if not assistant.quiet_mode:
                assistant.print_end(0)
            else:
                sys.exit(0)
        except:
            if not assistant.quiet_mode:
                assistant.print_end(1)
    else:
        assistant.logger.debug("len(args.file) = %s" % (len(args.file)))
        try:
            pool = ThreadPool(threads)
            results = pool.map(crc32.crc32, args.file)
            pool.close()
            pool.join()
            if not assistant.quiet_mode:
                assistant.print_end(0)
            else:
                sys.exit(0)
        except:
            if not assistant.quiet_mode:
                assistant.print_end(1)
    return None
