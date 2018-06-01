# !/usr/bin/python -u

"""
Copyright (C) 2018 LingoChamp Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import ntpath
from os import remove

from matplotlib import pyplot, dates
from matplotlib.ticker import FormatStrFormatter, FixedLocator
from os.path import exists
from pandas import to_datetime


def basicStyle():
    pyplot.gca().xaxis.set_major_formatter(dates.DateFormatter("%b %d"))
    pyplot.gca().xaxis.set_major_locator(dates.DayLocator())
    pyplot.gca().yaxis.set_major_formatter(FormatStrFormatter('%d'))
    pyplot.gcf().autofmt_xdate()
    pyplot.grid(axis='y', linestyle='-', linewidth=0.2, dash_capstyle='round')
    pyplot.ylabel("Count")


def addChart(x=[], y=[], title=""):
    x = [to_datetime(ts, unit='s') for ts in x]
    # print "%s %s %s" % (title, x, y)
    basicStyle()

    pyplot.plot(x, y, label=title)

    if title.__len__() > 0:
        pyplot.legend(ncol=2, loc='upper center',
                      bbox_to_anchor=[0.5, 1.1])


def endChartAndGetHtmlFragment(chartPath="", ymin=0, all_y=[]):
    pyplot.axes().set_ylim(ymin=ymin)

    all_y.sort()
    fixOverlap(all_y)
    pyplot.gca().yaxis.set_major_locator(FixedLocator(all_y))

    if exists(chartPath):
        print "remove old %s" % chartPath
        remove(chartPath)

    pyplot.savefig(chartPath)
    # pyplot.show()

    pyplot.close()
    return '<img src="cid:%s"/>' % path_leaf(chartPath)


def getSingleChartHtmlFragment(x=[], y=[], title='', chartPath=""):
    pyplot.title(title)
    addChart(x, y)

    return endChartAndGetHtmlFragment(chartPath, max(min(y) - 20, 0), y)


def fixOverlap(orderedValues=[]):
    minValue = orderedValues[0]
    maxValue = orderedValues[-1]

    gap = maxValue - minValue
    minGap = gap / 12

    if minGap <= 1:
        return

    before = minValue
    cursor = 1

    originValues = list(orderedValues)
    # keep min and max
    while cursor < originValues.__len__():
        candidate = originValues[cursor]
        if candidate - before < minGap:
            # force keep max but need consider gap
            if candidate == maxValue:
                if before in orderedValues:
                    orderedValues.remove(before)
            else:
                orderedValues.remove(candidate)
        else:
            before = candidate
        cursor += 1


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
