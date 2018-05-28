# coding: utf-8
import logging
import threading
import traceback

try:
    from django.db import close_old_connections
except ImportError:
    def close_old_connections():
        pass

LOGGER = logging.getLogger(__name__)


class EventDispatcher(object):
    def __init__(self):
        self._events = {}

    def __del__(self):
        self._events = None

    def __listener_executor(self, listener, args, kwargs):
        left_times = kwargs.pop('_left_times', 0)
        if left_times < 0:
            left_times = 0
        try:
            listener(*args, **kwargs)
        except:
            LOGGER.error({
                'listener': '%s.%s' % (getattr(listener, '__module__', 'None'), getattr(listener, '__name__', 'None')),
                'left_times(if > 0, will try in 100ms later)': left_times,
                'exceptions': traceback.format_exc(),
            })
            if left_times > 0:
                kwargs['_left_times'] = left_times - 1
                listener_thread = threading.Timer(0.1, function=self.__listener_executor, args=(listener, args, kwargs))
                listener_thread.setDaemon(True)
                listener_thread.start()
        finally:
            close_old_connections()

    def has_listener(self, event_type, listener):
        if event_type in self._events.keys():
            return listener in self._events[event_type]
        else:
            return False

    def dispatch_event(self, event_type, *args, **kwargs):
        if event_type in self._events.keys():
            listeners = self._events[event_type]

            for listener in listeners:
                times = getattr(listener, '_times', 3)
                kwargs['_left_times'] = kwargs.get('_left_times', times)
                listener_thread = threading.Thread(target=self.__listener_executor, args=(listener, args, kwargs))
                listener_thread.setDaemon(True)
                listener_thread.start()

    def add_event_listener(self, event_type, listener):
        if not self.has_listener(event_type, listener):
            listeners = self._events.get(event_type, [])
            listeners.append(listener)
            self._events[event_type] = listeners

    def remove_event_listener(self, event_type, listener):
        if self.has_listener(event_type, listener):
            listeners = self._events[event_type]
            if len(listeners) == 1:
                del self._events[event_type]
            else:
                listeners.remove(listener)
                self._events[event_type] = listeners


EventDispatcher = EventDispatcher()
