# coding: utf-8
import threading
import time

try:
    # needed to support Django >= 1.10 MIDDLEWARE
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    # needed to keep Django <= 1.9 MIDDLEWARE_CLASSES
    MiddlewareMixin = object


class EventPublishMiddleware(MiddlewareMixin):
    def __dispatch(self, dispatch_events):
        time.sleep(1)
        for dispatch_event in dispatch_events:
            if callable(dispatch_event):
                dispatch_event()

    def process_response(self, request, response):
        if int(response.status_code / 100) in [2, 3] and hasattr(request.session, '_dispatch_events'):
            dispatch_thread = threading.Thread(target=self.__dispatch, args=(request.session._dispatch_events,))
            dispatch_thread.setDaemon(True)
            dispatch_thread.start()
        return response
