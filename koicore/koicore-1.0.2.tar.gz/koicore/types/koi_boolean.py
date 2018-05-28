#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from ..koi_value import KoiValue


class KoiBoolean(KoiValue):
    def __init__(self, value: bool):
        super().__init__()
        self._value = value

    def as_boolean(self):
        return KoiBoolean(self._value)
