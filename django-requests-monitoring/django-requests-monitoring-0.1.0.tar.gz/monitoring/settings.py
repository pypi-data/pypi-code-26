from django.conf import settings

STATSD_HOST = getattr(settings, 'STATSD_HOST', '0.0.0.0')
STATSD_PORT = getattr(settings, 'STATSD_PORT', 9125)
STATSD_PREFIX = getattr(settings, 'STATSD_PREFIX', None)
STATSD_MAXUDPSIZE = getattr(settings, 'STATSD_MAXUDPSIZE', 512)
REQUEST_LATENCY_MIDDLEWARE_HIST = getattr(settings, 'REQUEST_LATENCY_MIDDLEWARE_HIST', "request.duration.seconds")
REQUEST_LATENCY_MIDDLEWARE_TAGS = getattr(settings, 'REQUEST_LATENCY_MIDDLEWARE_TAGS', [])