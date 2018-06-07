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
from os.path import exists

from humanfriendly import format_size
from matplotlib import pyplot, dates
from matplotlib.dates import date2num
from matplotlib.ticker import FixedLocator
from pandas import to_datetime

COLORS = ['aqua', 'black', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral',
          'cornflowerblue', 'crimson', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkkhaki',
          'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen',
          'darkslateblue', 'darkslategray', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray',
          'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold',
          'goldenrod', 'gray', 'green', 'greenyellow', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki',
          'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
          'lightgoldenrodyellow', 'lightgreen', 'lightgray', 'lightpink', 'lightsalmon', 'lightseagreen',
          'lightskyblue', 'lightslategray', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta',
          'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen',
          'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream',
          'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered',
          'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru',
          'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon',
          'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'snow',
          'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'white',
          'whitesmoke', 'yellow', 'yellowgreen']

COLOR_MAX_COUNT = COLORS.__len__()
COLOR_INDEX = 0

TYPE_COUNT = "count"
TYPE_PERCENT = "percent"
TYPE_DISK_SIZE = "diskSize"


class Chart:
    colorIndex = 0
    useColorGenerate = False

    def __init__(self, useColorGenerate=False):
        self.colorIndex = 0
        self.useColorGenerate = useColorGenerate

    def get_color(self):
        if self.colorIndex >= COLOR_MAX_COUNT:
            self.colorIndex = 0

        color = COLORS[self.colorIndex]
        self.colorIndex += 1
        return color

    def add_chart(self, x=[], y=[], title=""):
        x = [to_datetime(ts, unit='s') for ts in x]
        # print "%s %s %s" % (title, x, y)
        date_num_list = list()
        for num in x:
            date_num_list.append(date2num(num))
        pyplot.gca().xaxis.set_major_locator(FixedLocator(date_num_list))

        if self.useColorGenerate:
            pyplot.plot(x, y, label=title, color=self.get_color())
        else:
            pyplot.plot(x, y, label=title)

        if title.__len__() > 0:
            pyplot.legend(ncol=2, loc='upper center',
                          bbox_to_anchor=[0.5, 1.1])

    @staticmethod
    def done_with_html(chart_path="", ymin=0, all_y=[], chart_type=TYPE_COUNT):
        pyplot.gca().xaxis.set_major_formatter(dates.DateFormatter("%b %d"))
        pyplot.gcf().autofmt_xdate()
        pyplot.grid(axis='y', linestyle='-', linewidth=0.2, dash_capstyle='round')

        if chart_type == TYPE_PERCENT:
            pyplot.ylabel("Percent")
        elif chart_type == TYPE_DISK_SIZE:
            # use empty because of y-tick of size is occupied many space
            pyplot.ylabel("")
        else:
            pyplot.ylabel("Count")

        pyplot.axes().set_ylim(ymin=ymin)

        all_y.sort()
        fix_overlap(all_y)
        pyplot.gca().yaxis.set_major_locator(FixedLocator(all_y))

        if chart_type == TYPE_PERCENT:
            pyplot.gca().set_yticklabels(['{:3d}%'.format(x) for x in all_y])
        elif chart_type == TYPE_DISK_SIZE:
            pyplot.gca().set_yticklabels([format_size(y) for y in all_y])

        if exists(chart_path):
            print "remove old %s" % chart_path
            remove(chart_path)

        pyplot.savefig(chart_path)
        # pyplot.show()

        pyplot.close()
        return '<img src="cid:%s"/>' % path_leaf(chart_path)


def get_chart_html(x=[], y=[], title='', chart_path="", chart_type=TYPE_COUNT):
    chart = Chart()
    pyplot.title(title)
    chart.add_chart(x, y)

    return chart.done_with_html(chart_path, max(min(y) - 20, 0), y, chart_type)


def fix_overlap(ordered_values=[]):
    min_value = ordered_values[0]
    max_value = ordered_values[-1]

    gap = max_value - min_value
    min_gap = gap / 12

    if min_gap <= 1:
        return

    before = min_value
    cursor = 1

    origin_values = list(ordered_values)
    # keep min and max
    while cursor < origin_values.__len__():
        candidate = origin_values[cursor]
        if candidate - before < min_gap:
            # force keep max but need consider gap
            if candidate == max_value:
                if before in ordered_values:
                    ordered_values.remove(before)
            else:
                ordered_values.remove(candidate)
        else:
            before = candidate
        cursor += 1


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
