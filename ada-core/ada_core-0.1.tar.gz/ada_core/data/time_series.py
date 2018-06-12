"""
Author: qiacai
"""

from collections import OrderedDict

from ada_core.data.entry import Entry


class TimeSeries(OrderedDict):

    def __init__(self, dictTs: dict = None):
        super(TimeSeries, self).__init__()

        if dictTs and isinstance(dictTs, dict):

            for key in sorted(dictTs.keys()):
                if str.isdecimal(str(key)):
                    key = int(key)
                else:
                    continue
                if key <= 0:
                    continue
                value = dictTs.get(key)

                from ada_core import utils
                if not utils.isfloat(value):
                    continue
                else:
                    value = float(value)
                self.update({key: value})

    @property
    def start(self):
        """
        Return the earliest timestamp in the ts
        :return: int
        """
        return min(self.keys()) if self.keys() else None

    @property
    def end(self):
        """
        Return the latest timestamp in the ts
        :return: int
        """
        return max(self.keys()) if self.keys() else None

    def __repr__(self):
        return 'TimeSeries<start={0}, end={1}>'.format(repr(self.start), repr(self.end))

    def __str__(self):
        """
        :return string: Return string representation of time series
        """
        string_rep = ''
        for item in self.items():
            if not string_rep:
                string_rep += str(item)
            else:
                string_rep += ', ' + str(item)
        return 'TimeSeries([{}])'.format(string_rep)

    def getEntryList(self):
        entryList = []
        for key, value in self.items():
            entryList.append(Entry(key, value))
        return entryList

    def getValueList(self):
        return list(self.values())

    def getKeyList(self):
        return list(self.keys())