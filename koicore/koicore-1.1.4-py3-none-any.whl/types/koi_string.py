#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from koicore.koi_object import KoiObject
from koicore.types import KoiInteger, KoiBoolean


class KoiString(KoiObject):
    def __init__(self, value: str):
        super().__init__()
        self.value = value

    def to_boolean(self):
        if len(self.value) == 0:
            return KoiBoolean(False)

        else:
            return KoiBoolean(True)

    def to_character(self):
        pass

    def to_integer(self):
        if self.value.isdigit():
            return KoiInteger(int(self.value))

        else:
            return KoiInteger(0)

    def to_string(self):
        return KoiString(self.value)
