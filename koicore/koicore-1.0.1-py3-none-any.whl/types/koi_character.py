#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""""""

from ..koi_value import KoiValue


class KoiCharacter(KoiValue):
    def __init__(self, value: str):
        super().__init__()
        self._value = value[0]

    def as_character(self):
        return KoiCharacter(self._value)
