#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

import abc

from .types import KoiBoolean, KoiCharacter, KoiInteger, KoiString


class KoiObject(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._value = None
        self._type = self

    @abc.abstractmethod
    def as_boolean(self) -> KoiBoolean:
        """Returns the object as if it were a boolean."""
        pass

    @abc.abstractmethod
    def as_character(self) -> KoiCharacter:
        """Returns the object as if it were a character."""
        pass

    @abc.abstractmethod
    def as_integer(self) -> KoiInteger:
        """Returns the object as if it were an integer."""
        pass

    @abc.abstractmethod
    def as_string(self) -> KoiString:
        """Returns the object as if it were a string."""
        pass
