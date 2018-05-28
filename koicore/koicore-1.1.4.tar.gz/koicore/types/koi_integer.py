#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from koicore.koi_object import KoiObject


class KoiInteger(KoiObject):
    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def to_boolean(self):
        from .koi_boolean import KoiBoolean
        if self.value == 0:
            return KoiBoolean(False)

        else:
            return KoiBoolean(True)

    def to_character(self):
        pass

    def to_integer(self):
        return KoiInteger(self.value)

    def to_string(self):
        from .koi_string import KoiString
        return KoiString(f"{self.value}")
