#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from ..koi_value import KoiValue


class KoiString(KoiValue):
    def __init__(self, value: str):
        super().__init__()
        self._value = value

    def as_string(self):
        return KoiString(self._value)
