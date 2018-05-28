#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from ..koi_value import KoiValue


class KoiInteger(KoiValue):
    def __init__(self, value: int):
        super().__init__()
        self._value = value

    def as_integer(self):
        return KoiInteger(self._value)
