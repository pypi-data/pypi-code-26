#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


def get_chunksize(size, cpu, timefactor):
    return __div(size, max(cpu, cpu * __div(__div(size, timefactor), cpu)))
    # return __div(size, max(cpu, cpu * __div(__div(size, timefactor * cpu), cpu))) ?? TO TRY


def __div(x, y):
    return x // y + min(1, x % y)
