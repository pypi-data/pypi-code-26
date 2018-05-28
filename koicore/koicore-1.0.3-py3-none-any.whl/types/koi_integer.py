#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from koicore.koi_object import KoiObject
from koicore.types import KoiString, KoiBoolean


class KoiInteger(KoiObject):
    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def to_boolean(self):
        if self.value == 0:
            return KoiBoolean(False)

        else:
            return KoiBoolean(True)

    def to_character(self):
        pass

    def to_integer(self):
        return KoiInteger(self.value)

    def to_string(self):
        return KoiString(f"{self.value}")
