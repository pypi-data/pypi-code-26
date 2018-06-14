import time

from datadog import DogStatsd

from . import settings
from .statsd import StatsD

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass

statsd = StatsD(
    host=settings.STATSD_HOST,
    port=settings.STATSD_PORT,
    namespace=settings.STATSD_PREFIX
)


class RequestLatencyMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request._begun_at = time.time()

    def process_response(self, request, response):
        if not hasattr(request, '_begun_at'):
            return response
        took_seconds = time.time() - request._begun_at
        statsd.client.histogram(
            settings.REQUEST_LATENCY_MIDDLEWARE_HIST,
            took_seconds,
            tags=settings.REQUEST_LATENCY_MIDDLEWARE_TAGS + [
                'endpoint:{}'.format(request.path)
            ]
        )
        return response