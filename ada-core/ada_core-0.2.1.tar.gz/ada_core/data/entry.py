"""
Author: qiacai
"""


class Entry(object):

    def __init__(self, timestamp: int, value: float):
        self.timestamp = int(timestamp)
        self.value = float(value)

    def __repr__(self):
        return 'Entry<timestamp={0}, value={1}>'.format(repr(self.timestamp), repr(self.value))

    def __str__(self):
        return 'Entry(timestamp={0}, value={1})'.format(repr(self.timestamp), repr(self.value))

    def __eq__(self, other):
        if self.timestamp != other.timestamp or self.value !=other.timestamp:
            return False
        else:
            return True

    def __ge__(self, other):
        if self.value >= other.value:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.value > other.value:
            return True
        else:
            return False

    def __le__(self, other):
        if self.value <= other.value:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.value < other.value:
            return True
        else:
            return False

    def __round__(self, n=None):
        self.value = round(self.value, n)

    def __abs__(self):
        self.value = abs(self.value)