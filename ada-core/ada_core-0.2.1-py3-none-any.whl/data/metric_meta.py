"""
Author: qiacai
"""
import pytz


class MetricMeta(object):

    def __init__(self, name: str, timezone: str):
        self.name = name
        self.timezone = pytz.timezone(timezone)