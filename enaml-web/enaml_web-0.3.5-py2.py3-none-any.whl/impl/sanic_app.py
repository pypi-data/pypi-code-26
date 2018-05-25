"""
Copyright (c) 2018, Jairus Martin.

Distributed under the terms of the MIT License.

The full license is in the file COPYING.txt, distributed with this software.

Created on May 20, 2018

@author: jrm
"""
from sanic import Sanic
from functools import partial
from atom.api import Instance
from web.impl.lxml_app import LxmlApplication


class SanicApplication(LxmlApplication):
    """ An application based on MagicStack's uvloop
    
    """
    #: The event loop
    app = Instance(Sanic)

    def start(self):
        """ Start the application's main event loop.

        """
        self.app.run(host=self.interface,
                     port=self.port,
                     debug=self.debug)

    def stop(self):
        """ Stop the application's main event loop.

        """
        self.app.loop.stop()

    def deferred_call(self, callback, *args, **kwargs):
        """ Invoke a callable on the next cycle of the main event loop
        thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        if kwargs:
            callback = partial(callback, **kwargs)
        self.app.loop.call_soon(callback, *args)

    def timed_call(self, ms, callback, *args, **kwargs):
        """ Invoke a callable on the main event loop thread at a
        specified time in the future.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        if kwargs:
            callback = partial(callback, **kwargs)
        self.app.loop.call_later(ms/1000.0, callback, *args)

    def write_to_websocket(self, websocket, message):
        """ Send message data to a twisted websocket.

        Parameters
        -----------
        websocket :
            A websocket object for the given toolkit
        message : dict, str or bytes
            Data to send to the websocket

        """
        #: TODO
        raise NotImplementedError