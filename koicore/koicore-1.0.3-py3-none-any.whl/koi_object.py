#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

import abc


class KoiObject(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._type = self

    @abc.abstractmethod
    def to_boolean(self):  # -> KoiBoolean:
        """Returns the object as if it were a boolean."""
        from .types import KoiBoolean
        return KoiBoolean(False)

    @abc.abstractmethod
    def to_character(self):  # -> KoiCharacter:
        """Returns the object as if it were a character."""
        from .types import KoiCharacter
        return KoiCharacter("")

    @abc.abstractmethod
    def to_integer(self):  # -> KoiInteger:
        """Returns the object as if it were an integer."""
        from .types import KoiInteger
        return KoiInteger(0)

    @abc.abstractmethod
    def to_string(self):  # -> KoiString:
        """Returns the object as if it were a string."""
        from .types import KoiString
        return KoiString("")
