# -*- coding: utf-8 -*-
""" Various utilities used across the code base."""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import re
import inspect
from logging import getLogger

# 3rd party imports

# local imports


L = getLogger(__name__)


def remove_indent(text):
    """ Remove common indent from the text. """
    lines = text.split(os.linesep)

    min_indent = -1
    for line in (l for l in lines if l.strip()):
        without_indent = line.lstrip()
        indent = len(line) - len(without_indent)

        if min_indent == -1 or indent < min_indent:
            min_indent = indent

    return '\n'.join(l[min_indent:] for l in lines)


def iter_public_props(obj, predicate=None):
    """ Iterate over public properties of an object.

    :param Any obj:
        The object we want to get the properties of.
    :param function predicate:
        Additional predicate to filter out properties we're interested in. This
        function will be called on every property of the object with the
        property name and value as it arguments. If it returns True, the
        property will be yielded by this generator.
    """
    predicate = predicate or (lambda n, v: True)
    obj_type = type(obj)

    if inspect.isclass(obj):
        # This is a class
        for name, value in obj.__dict__.items():
            if isinstance(value, property):
                yield name, value
    else:
        # This is an instance
        for name in dir(obj):
            if name.startswith('_'):
                continue

            member = getattr(obj_type, name)
            if not isinstance(member, property):
                continue

            try:
                value = getattr(obj, name)
                if predicate(name, value):
                    yield name, value
            except AttributeError:
                pass


class ShellColors(object):
    """ Simple utility for coloring shell output """
    COLOR_RE = re.compile(r'\^(\d{1,2})')

    def __init__(self, opcode):
        """ Create color formatter using the given opcode """
        self.opcode = opcode

    def __call__(self, msg, *args, **kw):
        """
        :param msg: Message
        :param args: Positional arguments for msg.format()
        :param kw: Keyword arguments for msg.format()
        :return: Formatted string
        """
        if len(args) or len(kw):
            msg = msg.format(*args, **kw)

        return ShellColors.COLOR_RE.sub(self.opcode, msg)


cfmt = ShellColors(opcode=r'\033[\1m')
