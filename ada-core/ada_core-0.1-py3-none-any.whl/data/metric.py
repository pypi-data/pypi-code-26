"""
Author: qiacai
"""


from ada_core.data.time_series import TimeSeries
from ada_core.data.metric_meta import MetricMeta


class Metric(object):

    def __init__(self, time_series: TimeSeries, metric_meta: MetricMeta):
        self.time_series = time_series
        self.metric_meta = metric_meta

    def __len__(self):
        return len(self.time_series)