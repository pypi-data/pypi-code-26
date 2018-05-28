# coding: utf-8
from functools import wraps

from EventAggregator.event_dispatcher import EventDispatcher
from django.contrib.sessions.backends.db import SessionBase


class EventAggregator:
    @staticmethod
    def publish(message, session: SessionBase = None):
        """
        :param message: 发布的消息
        :param session: 有值时，对应的响应(response)没有异常时发布; 为None立即发布
        :return:
        """
        if isinstance(session, SessionBase):
            if not hasattr(session, '_dispatch_events'):
                session._dispatch_events = []
            session._dispatch_events.append(lambda: EventDispatcher.dispatch_event(type(message), message))
        else:
            EventDispatcher.dispatch_event(type(message), message)

    @staticmethod
    def subscribe(message_class, handler, times=3):
        """
        :param message_class: 
        :param handler: 
        :param times: 失败时，重试的次数， 取值>=0 
        :return: 
        """
        handler._times = times
        EventDispatcher.add_event_listener(message_class, handler)

    @staticmethod
    def unsubscribe(message_class, handler):
        EventDispatcher.remove_event_listener(message_class, handler)


def subscriber(message_class, retry_times=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        EventAggregator.subscribe(message_class, func, retry_times)
        return wrapper

    return decorator
