#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from koicore.koi_object import KoiObject
from koicore.types import KoiInteger, KoiString


class KoiBoolean(KoiObject):
    def __init__(self, value: bool):
        super().__init__()
        self.value = value

    def to_boolean(self):
        return KoiBoolean(self.value)

    def to_character(self):
        pass

    def to_integer(self):
        if self.value:
            return KoiInteger(1)

        else:
            return KoiInteger(0)

    def to_string(self):
        return KoiString(f"{self.value}")
