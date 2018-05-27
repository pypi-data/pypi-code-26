#!/usr/bin/python
# -*- coding: UTF-8 -*-
r"""
@author: Martin Klapproth <martin.klapproth@googlemail.com>
"""
import fnmatch
import logging
from copy import deepcopy

from os import walk
from os.path import abspath, join

logger = logging.getLogger(__name__)


def locate(pattern, root, followlinks=True):
    for path, _, files in walk(abspath(root), followlinks=followlinks):
        for filename in fnmatch.filter(files, pattern):
            yield join(path, filename)


def dict_merge(a, b):
    """
    recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and b have a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.
    :param a: dict
    :param b: dict (takes precedence if same key exists also in a)
    :return:
    """
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.items():
        if k in result and isinstance(result[k], dict):
            result[k] = dict_merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result


def interactive_select(items, description=None):
    items.sort()

    if len(items) == 1:
        result = items[0]
        print("Automatically selecting: %s" % result)
        return result
    else:
        if description:
            print(description)
        else:
            print("Please select an option")

        item_mapping = {}
        idx = 1
        for p in items:
            print("%2i: %s" % (idx, p))
            item_mapping[idx] = p
            idx += 1

        while True:
            try:
                item_nr = int(input("Option number? "))
            except ValueError:
                continue
            try:
                return item_mapping[item_nr]
            except KeyError:
                print("Invalid option selected")
                continue
