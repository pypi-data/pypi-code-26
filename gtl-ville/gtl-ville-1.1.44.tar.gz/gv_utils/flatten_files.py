#!/usr/bin/env python3

import os
import shutil
import time


def flatten(oldfilespath, newbasepath):
    for year in os.listdir(oldfilespath):
        yearpath = os.path.join(oldfilespath, year)
        if not os.path.isdir(yearpath):
            continue
        for month in os.listdir(yearpath):
            monthpath = os.path.join(yearpath, month)
            if not os.path.isdir(monthpath):
                continue
            for day in os.listdir(monthpath):
                daypath = os.path.join(monthpath, day)
                if not os.path.isdir(daypath):
                    continue
                for pbfile in os.listdir(daypath):
                    try:
                        filepath = os.path.join(daypath, pbfile)
                        shutil.copy(filepath, __get_full_path(newbasepath, year, month, day))
                    except:
                        continue


def __get_full_path(pbbasepath, year, month, day):
    dayofyear = str(time.strptime(year + '/' + month + '/' + day, '%Y/%m/%d').tm_yday)
    fullpath = os.path.join(pbbasepath, year, dayofyear)
    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
    return fullpath
