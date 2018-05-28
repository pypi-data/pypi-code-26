#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from koicore import KoiObject


class KoiVariable(KoiObject):
    def __init__(self, value: KoiObject):
        super().__init__()
        self.value = value
        self.type_ = type(self.value)

    def to_boolean(self):
        return self.value.to_boolean()

    def to_character(self):
        return self.value.to_character()

    def to_integer(self):
        return self.value.to_integer()

    def to_string(self):
        return self.value.to_string()
