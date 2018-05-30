__all__ = [
    "MetricId",
    "Recorder",
    "LogTransport",
    "InMemoryTransport",
    "RiemannTransport",
    "CompositeTransport",
    "Gauge",
    "Summary",
    "Counter",
    "Timer",
    "Metrics",
]


from collections import defaultdict, namedtuple
import collections
import json
import logging
import timeit

from ._deprecation import deprecated

from riemann_client.client import Client
from riemann_client.riemann_pb2 import Msg
from riemann_client.transport import TCPTransport


MetricId = namedtuple("MetricId", ["name", "tags", "attributes"])


class Metric:
    def __init__(self, service, value, ttl, tags, fields):
        self.id = self._id(service, tags, fields)
        self.value = value
        self.name = service
        self.tags = tags
        self.ttl = ttl
        self.attributes = {str(k): str(v) for k, v in fields.items()}

    def _id(self, service_name, tags, fields):
        return MetricId(service_name, frozenset(tags), frozenset(fields.items()))


class Recorder:
    """
    Base type for recorders - objects that forward metrics over a transport
    """

    def send(self, metric, value, transport, suffix=""):
        ttl = metric.ttl
        event = {
            "tags": metric.tags,
            "attributes": metric.attributes,
            "service": metric.name + suffix,
            "metric_f": value,
        }
        if ttl is not None:
            event["ttl"] = ttl

        transport.send_event(event)


class LogTransport:

    """
    Simple Transport that sprints metrics to the log. Useful for development
    environments
    """

    def __init__(self):
        self._logger = logging.getLogger("metrics")

    def send_event(self, event):
        self._logger.info(
            "metric %s=%s (%s)",
            event["service"],
            event["metric_f"],
            json.dumps(event.get("attributes")),
        )

    def flush(self, is_closing):
        pass


class InMemoryTransport:

    """
    Dummy transport that keeps a copy of the last flushed batch of events. This
    is used to store the data for the stats endpoints.
    """

    def __init__(self):
        self.current_batch = []
        self.last_batch = []

    def send_event(self, event):
        self.current_batch.append(event)

    def flush(self, is_closing):
        self.last_batch = list(self.current_batch)
        self.current_batch = []


class RiemannTransport:

    """
    Transport that sends metrics to a Riemann server.
    """

    def __init__(self, host="localhost", port="5555", timeout=5):
        self.host = host
        self.port = port

        self.transport = TCPTransport(self.host, self.port, timeout)
        self._new_message()
        self._connected = False

    def send_event(self, event):
        riemann_event = Client.create_event(event)
        self._message.events.add().MergeFrom(riemann_event)

    def _ensure_connected(self):
        # This is just to avoid logging about failure on the first try
        if not self._connected:
            self.transport.connect()
            self._connected = True

    def flush(self, is_closing):
        self._ensure_connected()
        try:
            self.transport.send(self._message)
        except Exception as e:
            self.transport.disconnect()
            logging.warning("Failed to flush metrics to riemann")
            self.transport.connect()
            try:
                self.transport.send(self._message)
            except Exception as e:
                logging.error("Failed twice to flush metrics to riemann", exc_info=True)
        if is_closing:
            self.transport.disconnect()
        self._new_message()

    def _new_message(self):
        self._message = Msg()

    @deprecated("Should be no need to check, will reconnect automatically")
    def is_connected(self):
        """Check whether the transport is connected."""
        return True


class CompositeTransport:

    """
    Transport that wraps two or more transports and forwards events to all of
    them.
    """

    def __init__(self, *args):
        self._transports = args

    def send_event(self, event):
        for t in self._transports:
            t.send_event(event)

    def flush(self, is_closing):
        for t in self._transports:
            t.flush(is_closing)


class Summary(Recorder):
    """
    Summarys record the range of a value across a set of datapoints,
    eg response time, items cleared from cache, and forward aggregated
    metrics to describe that range.
    """

    def __init__(self, source):
        self._source = source
        self._reset()

    def _reset(self):
        self._metrics = defaultdict(list)

    def record(self, service_name, value, ttl=None, tags=[], attributes=dict()):
        if self._source:
            attributes["source"] = self._source
        metric = Metric(service_name, value, ttl, tags, attributes)
        self._metrics[metric.id].append(metric)

    def flush(self, transport):
        for metric in self._metrics.values():

            first = metric[0]
            _min = first.value
            _max = first.value
            _mean = 0
            _count = 0
            _total = 0

            for measurement in metric:
                _count = _count + 1
                _total = _total + measurement.value
                _max = max(_max, measurement.value)
                _min = min(_min, measurement.value)

            _mean = _total / _count

            self.send(first, _min, transport, ".min")
            self.send(first, _max, transport, ".max")
            self.send(first, _mean, transport, ".mean")
            self.send(first, _count, transport, ".count")

        self._reset()


class Counter(Recorder):

    """
    Counters record incrementing or decrementing values, eg. Events Processed,
    error count, cache hits.
    """

    def __init__(self, source):
        self._source = source
        self._counters = collections.defaultdict(list)

    def record(self, service_name, value, ttl, tags, attributes):
        if self._source:
            attributes["source"] = self._source
        metric = Metric(service_name, value, ttl, tags, attributes)

        self._counters[metric.id].append(metric)

    def flush(self, transport):
        for counter in self._counters.values():
            count = sum(m.value for m in counter)
            self.send(counter[0], count, transport)
        self._counters = defaultdict(list)


class Gauge(Recorder):

    """
    Gauges record scalar values at a single point in time, eg. queue size,
    active sessions, and forward only the latest value.
    """

    def __init__(self, source):
        self._source = source
        self._gauges = dict()

    def record(self, service_name, value, ttl, tags, attributes):
        if self._source:
            attributes["source"] = self._source
        metric = Metric(service_name, value, ttl, tags, attributes)

        self._gauges[metric.id] = metric

    def flush(self, transport):
        for gauge in self._gauges.values():
            self.send(gauge, gauge.value, transport)
        self._gauges = dict()


class Timer:

    """
    Timers provide a context manager that times an operation and records a
    gauge with the elapsed time.
    """

    def __init__(self, service_name, ttl, tags, attributes, histogram):
        self.service_name = service_name
        self.ttl = ttl
        self.tags = tags
        self.attributes = attributes
        self.recorder = histogram

    def __enter__(self):
        self.start = timeit.default_timer()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        elapsed = timeit.default_timer() - self.start
        self.recorder.record(
            self.service_name, elapsed, self.ttl, self.tags, self.attributes
        )


class Metrics:
    def __init__(self, transport, source=None):
        self._transport = transport
        self._gauges = Gauge(source)
        self._histograms = Summary(source)
        self._counters = Counter(source)

    def recordGauge(self, service_name, value, ttl=None, tags=[], **kwargs):
        self._gauges.record(service_name, value, ttl, tags, kwargs)

    def incrementCounter(self, service_name, value=1, ttl=None, tags=[], **kwargs):
        self._counters.record(service_name, value, ttl, tags, kwargs)

    def decrementCounter(self, service_name, value=1, ttl=None, tags=[], **kwargs):
        self._counters.record(service_name, 0 - value, ttl, tags, kwargs)

    def time(self, service_name, ttl=None, tags=[], **kwargs):
        return Timer(service_name, ttl, tags, kwargs, self._histograms)

    def recordSummary(self, service_name, value, ttl=None, tags=[], **kwargs):
        self._histograms.record(service_name, 0 - value, ttl, tags, kwargs)

    def flush(self, is_closing=False):
        self._gauges.flush(self._transport)
        self._counters.flush(self._transport)
        self._histograms.flush(self._transport)
        self._transport.flush(is_closing)
