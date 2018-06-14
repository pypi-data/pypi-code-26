#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Class and methods used to parse command-line arguments.

"""

import os
import re
import sys
import textwrap
from argparse import HelpFormatter, ArgumentTypeError, Action, ArgumentParser
from ctypes import c_char_p
from datetime import datetime as dt
from gettext import gettext
from multiprocessing import Value


class MultilineFormatter(HelpFormatter):
    """
    Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __init__(self, prog):
        # Overload the HelpFormatter class.
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _fill_text(self, text, width, indent):
        # Rewrites the _fill_text method to support multiline description.
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text

    def _split_lines(self, text, width):
        # Rewrites the _split_lines method to support multiline helps.
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text


class DirectoryChecker(Action):
    """
    Custom action class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, list):
            checked_vals = [self.directory_checker(x) for x in values]
        else:
            checked_vals = self.directory_checker(values)
        setattr(namespace, self.dest, checked_vals)

    @staticmethod
    def directory_checker(path):
        """
        Checks if the supplied directory exists. The path is normalized without trailing slash.

        :param str path: The path list to check
        :returns: The same path list
        :rtype: *str*
        :raises Error: If one of the directory does not exist

        """
        path = os.path.abspath(os.path.normpath(path))
        if not os.path.isdir(path):
            msg = 'No such directory: {}'.format(path)
            raise ArgumentTypeError(msg)
        return path


def keyval_converter(pair):
    """
    Checks the key value syntax.

    :param str pair: The key/value pair to check
    :returns: The key/value pair
    :rtype: *tuple*
    :raises Error: If invalid pair syntax

    """
    pattern = re.compile(r'([^=]+)=([^=]+)(?:,|$)')
    if not pattern.search(pair):
        msg = 'Bad argument syntax: {}'.format(pair)
        raise ArgumentTypeError(msg)
    key, regex = pattern.search(pair).groups()
    try:
        regex = re.compile(regex)
    except re.error:
        msg = 'Bad regex syntax: {}'.format(regex)
        raise ArgumentTypeError(msg)
    return key, regex


def processes_validator(value):
    """
    Validates the max processes number.

    :param str value: The max processes number submitted
    :return:
    """
    pnum = int(value)
    if pnum < 1 and pnum != -1:
        msg = 'Invalid processes number. Should be a positive integer or "-1".'
        raise ArgumentTypeError(msg)
    if pnum == -1:
        # Max processes = None corresponds to cpu.count() in Pool creation
        return None
    else:
        return pnum


class _ArgumentParser(ArgumentParser):
    def error(self, message):
        """
        Overwrite the original method to change exist status.

        """
        self.print_usage(sys.stderr)
        self.exit(-1, gettext('%s: error: %s\n') % (self.prog, message))


class ProcessContext(object):
    """
    Encapsulates the processing context/information for child process.

    :param dict args: Dictionary of argument to pass to child process
    :returns: The processing context
    :rtype: *ProcessContext*

    """

    def __init__(self, args):
        assert isinstance(args, dict)
        for key, value in args.items():
            setattr(self, key, value)


class COLORS:
    """
    Background colors for print statements

    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[1;32m'
    WARNING = '\033[1;34m'
    FAIL = '\033[1;31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Print(object):
    """
    Class to manage and dispatch print statement depending on log and debug mode.

    """
    LOG = None
    DEBUG = False
    ALL = False
    CMD = None
    BUFFER = Value(c_char_p, '')
    LOGFILE = None

    @staticmethod
    def init(log, debug, cmd, all):
        Print.LOG = log
        Print.DEBUG = debug
        Print.CMD = cmd
        Print.ALL = all
        logname = '{}-{}'.format(Print.CMD, dt.now().strftime("%Y%m%d-%H%M%S"))
        if Print.LOG:
            logdir = Print.LOG
            if not os.path.isdir(Print.LOG):
                os.makedirs(Print.LOG)
        else:
            logdir = os.getcwd()
        Print.LOGFILE = os.path.join(logdir, logname + '.log')

    @staticmethod
    def print_to_stdout(msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

    @staticmethod
    def print_to_logfile(msg):
        with open(Print.LOGFILE, 'a+') as f:
            for color in COLORS.__dict__.values():
                msg = msg.replace(color, '')
            f.write(msg)

    @staticmethod
    def progress(msg):
        if Print.LOG:
            Print.print_to_stdout(msg)
        elif not Print.DEBUG:
            Print.print_to_stdout(msg)

    @staticmethod
    def command(msg):
        if Print.LOG:
            Print.print_to_logfile(msg)
        elif Print.DEBUG:
            Print.print_to_stdout(msg)

    @staticmethod
    def summary(msg):
        if Print.LOG:
            Print.print_to_stdout(msg)
            Print.print_to_logfile(msg)
        else:
            Print.print_to_stdout(msg)

    @staticmethod
    def info(msg):
        if Print.LOG:
            Print.print_to_stdout(msg)

    @staticmethod
    def debug(msg):
        if Print.DEBUG:
            if Print.LOG:
                Print.print_to_logfile(msg)
            else:
                Print.print_to_stdout(msg)

    @staticmethod
    def error(msg):
        if Print.LOG:
            Print.print_to_logfile(msg)
        else:
            Print.print_to_stdout(msg)

    @staticmethod
    def success(msg):
        if Print.LOG:
            Print.print_to_logfile(msg)
        else:
            Print.print_to_stdout(msg)
