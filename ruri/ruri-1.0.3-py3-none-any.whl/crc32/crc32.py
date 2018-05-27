#!/usr/bin/env python3
# Released under the GPL license http://www.gnu.org/licenses/gpl-3.0.txt

import argparse
import datetime
import logging
import os
import re
import sys
import zlib
from multiprocessing.dummy import Pool as ThreadPool
from timeit import default_timer as timer

from progressbar import ProgressBar, Percentage, Bar, AdaptiveETA, AdaptiveTransferSpeed

VERSION = "1.0.3"
assistant = None


class Assistant(object):
    COLOR_NULL = "\x1b[00;00m"
    COLOR_RED = "\x1b[31;01m"
    COLOR_GREEN = "\x1b[32;01m"
    COLOR_YELLOW = "\x1b[33;01m"
    COLOR_BLUE = "\x1b[34;01m"
    COLOR_PURPLE = "\x1b[35;01m"
    CLEAN_LINE = "\033[F\033[0K"
    WIDGETS = [
        Percentage(), " ",
        Bar(), " ",
        AdaptiveETA(), " ",
        AdaptiveTransferSpeed()
    ]
    logger = logging.getLogger("crc32")

    def __init__(self, quiet_mode):
        self.start = timer()
        self.successful = 0
        self.not_found = 0
        self.no_match = 0
        self.failed = 0
        self.quiet_mode = quiet_mode
        if quiet_mode:
            self.COLOR_NULL = ""
            self.COLOR_RED = ""
            self.COLOR_GREEN = ""
            self.COLOR_YELLOW = ""
            self.COLOR_BLUE = ""
            self.COLOR_PURPLE = ""

    def print_end(self, exit_code):
        end = timer()
        time = end - self.start
        time_str = str(datetime.timedelta(seconds=time))
        str_length = 1

        if self.successful >= self.not_found and self.successful >= self.no_match and self.successful >= self.failed:
            str_length = len(str(self.successful))
        elif self.not_found >= self.successful and self.not_found >= self.no_match and self.not_found >= self.failed:
            str_length = len(str(self.not_found))
        elif self.no_match >= self.successful and self.no_match >= self.not_found and self.no_match >= self.failed:
            str_length = len(str(self.no_match))
        elif self.failed >= self.successful and self.failed >= self.not_found and self.failed >= self.no_match:
            str_length = len(str(self.failed))

        self.logger.info(
            "%s%s%s %s%s%s %s%s%s %s%s%s %s%s%s\n" % (
                self.COLOR_GREEN,
                str(self.successful).rjust(str_length, '0'),
                self.COLOR_NULL,
                self.COLOR_YELLOW,
                str(self.not_found).rjust(str_length, '0'),
                self.COLOR_NULL,
                self.COLOR_RED,
                str(self.no_match).rjust(str_length, '0'),
                self.COLOR_NULL,
                self.COLOR_PURPLE,
                str(self.failed).rjust(str_length, '0'),
                self.COLOR_NULL,
                self.COLOR_BLUE,
                time_str,
                self.COLOR_NULL
            )
        )
        sys.exit(exit_code)


def main():
    global assistant, VERSION
    parser = argparse.ArgumentParser(description="CRC32")
    parser.add_argument("-r", "--recursive", help="work recursively", action="store_true")
    parser.add_argument("-t", "--threads", help="override the ammount of threads", type=int, default=1)
    parser.add_argument("-v", "--verbose", help="output level", action="store_true")
    parser.add_argument("-q", "--quiet", help="Do not print progressbars.", action="store_true")
    parser.add_argument("--version", help="Print the version number, and exit.", action="version",
                        version="%(prog)s version " + VERSION)
    parser.add_argument("file", nargs='+', help="The file(s) you need CRC'ed")
    try:
        args = parser.parse_args()
    except:
        assistant = Assistant(False)
        assistant.print_end(8)

    assistant = Assistant(args.quiet)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s]\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    threads = args.threads
    assistant.logger.debug("Threads set at %s" % str(args.threads))

    if args.recursive:
        assistant.logger.warning(
            "%sWARNING%s\t%sExperimental feature%s" % (
                assistant.COLOR_PURPLE,
                assistant.COLOR_NULL,
                assistant.COLOR_RED,
                assistant.COLOR_NULL
            )
        )
        assistant.logger.debug("len(args.file) = %s" % (len(args.file)))
        file_set = set()
        for root_dir in args.file:
            for root, dirs, files in os.walk(root_dir):
                for file in files:
                    rel_dir = os.path.relpath(root, ".")
                    rel_file = os.path.join(rel_dir, file)
                    file_set.add(rel_file)
            pool = ThreadPool(threads)
            results = pool.map(crc32, file_set)
            pool.close()
        pool.join()
        assistant.logger.debug("results = %s" % results)
    else:
        assistant.logger.debug("len(args.file) = %s" % (len(args.file)))
        pool = ThreadPool(threads)
        results = pool.map(crc32, args.file)
        pool.close()
        pool.join()
    return None


def crc32(file):
    crc_calculated = None
    crc_found = None
    try:
        crc_calculated = crc32_checksum(file)
        assistant.logger.debug("crc_calculated: %s" % str(crc_calculated))
        crc_found = re.split("([a-fA-F0-9]{8})", file)[-2]
        assistant.logger.debug("crc_found: %s" % str(crc_found))
    except (IndexError, ValueError) as e:
        assistant.logger.debug("Error: %s" % str(e))
        assistant.not_found += 1
        if not assistant.quiet_mode:
            assistant.logger.warning(
                "%s%s%s%s\t%s" % (
                    assistant.CLEAN_LINE,
                    assistant.COLOR_YELLOW,
                    crc_calculated,
                    assistant.COLOR_NULL,
                    file
                )
            )
        else:
            print(
                "%s\t%s" % (
                    crc_calculated,
                    file
                )
            )

    except (IOError, OSError) as e:
        assistant.logger.debug("Error: %s" % str(e))
        assistant.failed += 1
        if not assistant.quiet_mode:
            assistant.logger.error(
                "%s%sERROR%s\t%s\t%s\t%sAT%s\t%s" % (
                    assistant.CLEAN_LINE,
                    assistant.COLOR_PURPLE,
                    assistant.COLOR_NULL,
                    e.errno,
                    e.strerror,
                    assistant.COLOR_PURPLE,
                    assistant.COLOR_NULL,
                    file
                )
            )
        else:
            print(
                "%s\t%s\tAT\t%s" % (
                    e.errno,
                    e.strerror,
                    file
                )
            )
    else:
        if crc_calculated == crc_found.upper():
            color = assistant.COLOR_GREEN
            assistant.successful += 1
        else:
            color = assistant.COLOR_RED
            assistant.not_found += 1

        filename_split = file.split(crc_found)

        if not assistant.quiet_mode:
            assistant.logger.info(
                "%s%s%s%s\t%s%s%s%s%s" % (
                    assistant.CLEAN_LINE,
                    color,
                    crc_calculated,
                    assistant.COLOR_NULL,
                    filename_split[0],
                    color,
                    crc_found,
                    assistant.COLOR_NULL,
                    filename_split[1]
                )
            )
        else:
            print(
                "%s\t%s" % (
                    crc_calculated,
                    file
                )
            )

    return file


def crc32_checksum(filename):
    assistant.logger.debug("filename: %s" % filename)
    crc = 0
    file = open(filename, "rb")
    buff_size = 65536
    done = 0
    size = os.path.getsize(filename)
    assistant.logger.debug("size: %s" % str(size))
    pbar = ProgressBar(widgets=assistant.WIDGETS, max_value=size)
    if not assistant.quiet_mode:
        pbar.start()
    try:
        while True:
            data = file.read(buff_size)
            done += buff_size
            if not data:
                if not assistant.quiet_mode:
                    pbar.finish()
                assistant.logger.debug("data: %s" % str(data))
                break
            else:
                if not assistant.quiet_mode:
                    try:
                        pbar.update(done)
                    except:
                        pass
            crc = zlib.crc32(data, crc)
    except KeyboardInterrupt:
        if not assistant.quiet_mode:
            pbar.finish()
        assistant.logger.debug("crc32_checksum: KeyboardInterrupt")
        file.close()
        return None
    assistant.logger.debug("done: %s" % str(done))
    file.close()
    if crc < 0:
        crc &= 2 ** 32 - 1
    return "%.8X" % (crc)


if __name__ == '__main__':
    try:
        main()
    except:
        assistant.print_end(1)
    else:
        if not assistant.quiet_mode:
            assistant.print_end(0)
        else:
            sys.exit(0)
