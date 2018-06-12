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
from datetime import datetime
from gettext import gettext


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


class Colors:
    """
    Background colors for print statements

    """

    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[1;32m'
        self.WARNING = '\033[1;34m'
        self.FAIL = '\033[1;31m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'


COLORS = Colors()


class Print(object):
    """
    Class to manage and dispatch print statement depending on log and debug mode.

    """

    def __init__(self, log, debug):
        self._log = log
        self._debug = debug
        self._colors = COLORS.__dict__
        logname = 'XIOFileChecker-{}.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S"))
        if self._log:
            if not os.path.isdir(self._log):
                os.makedirs(self._log)
            self._logfile = os.path.join(self._log, logname)
        else:
            self._logfile = os.path.join(os.getcwd(), logname)

    @staticmethod
    def print_to_stdout(msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

    def print_to_logfile(self, msg):
        with open(self._logfile, 'a+') as f:
            for color in self._colors.values():
                msg = msg.replace(color, '')
            f.write(msg)

    def progress(self, msg):
        if self._log:
            self.print_to_stdout(msg)
        elif not self._debug:
            self.print_to_stdout(msg)

    def command(self, msg):
        if self._log:
            self.print_to_logfile(msg)
        elif self._debug:
            self.print_to_stdout(msg)

    def summary(self, msg):
        if self._log:
            self.print_to_stdout(msg)
            self.print_to_logfile(msg)
        else:
            self.print_to_stdout(msg)

    def info(self, msg):
        if self._log:
            self.print_to_stdout(msg)

    def debug(self, msg):
        if self._debug:
            if self._log:
                self.print_to_logfile(msg)
            else:
                self.print_to_stdout(msg)

    def error(self, msg):
        if self._log:
            self.print_to_logfile(msg)
        else:
            self.print_to_stdout(msg)

    def success(self, msg):
        if self._log:
            self.print_to_logfile(msg)
        else:
            self.print_to_stdout(msg)
