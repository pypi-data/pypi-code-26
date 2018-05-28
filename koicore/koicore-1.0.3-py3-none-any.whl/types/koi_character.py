#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from koicore.koi_object import KoiObject


class KoiCharacter(KoiObject):
    def __init__(self, value: str):
        super().__init__()
        self.value = value[0]

    def to_boolean(self):
        pass

    def to_character(self):
        return KoiCharacter(self.value)

    def to_integer(self):
        pass

    def to_string(self):
        pass
