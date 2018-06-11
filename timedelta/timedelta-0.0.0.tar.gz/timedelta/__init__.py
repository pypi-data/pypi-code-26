#!/usr/bin/env python
import datetime
from public import public

# https://docs.python.org/3/library/datetime.html#timedelta-objects


@public
class Total:
    total_seconds = None

    def __init__(self, total_seconds):
        self.total_seconds = total_seconds

    @property
    def seconds(self):
        return int(self.total_seconds)

    @property
    def minutes(self):
        return int(self.seconds / 60)

    @property
    def hours(self):
        return int(self.minutes / 60)

    @property
    def days(self):
        return int(self.hours / 24)

    @property
    def weeks(self):
        return int(self.days / 7)

    @property
    def months(self):
        return int(self.days / 30)

    @property
    def years(self):
        return int(self.days / 365)


@public
class Timedelta(datetime.timedelta):
    def __new__(self, *args, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        if args:
            seconds = args[0].total_seconds()
            microseconds = args[0].microseconds
        return datetime.timedelta.__new__(self, days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    @property
    def total(self):
        return Total(self.total_seconds())
