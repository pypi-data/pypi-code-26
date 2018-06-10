# -*- coding: utf-8 -*-
""" This module contains commons methods which has no dependencies (except for
the base python library) and thus are usable in every part of the software.

The methods included in this modules are all mathematical-related functions.
"""


def is_int(number: str) -> bool:
    """ Check if a string is an integer. """
    try:
        int(number)
        return True if "." not in number else False
    except ValueError:
        return False


if __name__ == "__main__":
    pass
