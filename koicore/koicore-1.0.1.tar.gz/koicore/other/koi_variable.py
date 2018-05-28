#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from ..koi_object import KoiObject


class KoiVariable(KoiObject):
    def __init__(self, value: KoiObject):
        super().__init__()
        self._value = value
        self._type = type(value)

    def as_boolean(self):
        return self._value.as_boolean()

    def as_character(self):
        return self._value.as_character()

    def as_integer(self):
        return self._value.as_integer()

    def as_string(self):
        return self._value.as_string()
