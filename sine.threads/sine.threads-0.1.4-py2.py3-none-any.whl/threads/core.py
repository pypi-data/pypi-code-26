# coding=utf-8
'''
custom thread objects.

Threads like threading.Thread but can be stopped softly through self-check,
or restarted with the same target.
'''

import threading
import inspect

class StoppableThread(threading.Thread):
    '''
    thread with a stop() method.

    A threading.Event will be set as an attribute,
    and passed to the target function via @parameter kwargs,
    with default name 'stop_event'. The thread itself has to
    check the event regularly by i.e. stop_event.is_set(),
    and stop itself when the event is set.

    Note: you should not change the event.
    '''

    def __init__(self, group=None, target=None, name=None, args=(),
                 kwargs=None, verbose=None, event_name='stop_event'):
        '''
        arguments are same as threading.Thread with additional event_name

        this assert the target function (if not None)
        whether it has the argument named the event_name
        or a keywords argument to accept the event.
        '''
        if target != None:
            spec = inspect.getargspec(target)
            if spec.keywords == None and event_name not in spec.args:
                raise ValueError('target function has neighter \
**kwargs or argument \'' + event_name + '\'')
        self._stop_event = threading.Event()
        self.__setattr__(event_name, self._stop_event)
        if kwargs == None:
            kwargs = {}
        kwargs[event_name] = self._stop_event
        super(StoppableThread, self).__init__(group, target, name, args,
                                              kwargs, verbose)
        return

    def stop(self):
        '''set the event.'''
        self._stop_event.set()
        return

    def stopped(self):
        '''whether the event is set'''
        return self._stop_event.is_set()

class ReStartableThread(object):
    '''
    provide restartable feature in addition to StoppableThread.

    defaults to set setDaemon(True).
    
    new instance of Thread object will be created after stop(),
    so you should set the properties again.
    '''
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._started = False
        self._thread = StoppableThread(*self._args, **self._kwargs)
        self._thread.setDaemon(True)
        self._thread0 = self._thread
        return

    def start(self):
        '''call stop() the thread if started, then start the thread.'''
        if self._started:
            self.stop()
        self._started = True
        self._thread.start()
        return

    def stop(self):
        '''stop the thread and create new instance.'''
        if self._started:
            self._thread.stop()
        self._started = False
        self._thread0 = self._thread
        self._thread = StoppableThread(*self._args, **self._kwargs)
        self._thread.setDaemon(True)
        return

    def join(self, timeout=None):
        '''join the new instance after started, else join the old one'''
        if self._started:
            self._thread.join(timeout)
        else:
            self._thread0.join(timeout)

    def __getattr__(self, name):
        '''get method or attributes (e.g. the event) from the thread instance if not found.'''
        return self._thread.__getattribute__(name)
