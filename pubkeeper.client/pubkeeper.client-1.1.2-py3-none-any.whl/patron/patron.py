"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.function_table import FunctionTable
from pubkeeper.topic import Topic
from tornado import ioloop
from uuid import uuid4

__all__ = ['Patron']
PatronFT = FunctionTable()


class Patron(Topic):
    def __init__(self, topic, callback, patron_id=None, io_loop=None, **kwargs):
        super().__init__(topic)

        self.patron_id = patron_id or uuid4().hex
        self._callback = callback
        self._patroning = {}
        self._ciphers = {}
        self._kwargs = kwargs

        if io_loop is None:
            self._io_loop = ioloop.IOLoop.current()
        else:
            self._io_loop = io_loop

    def configure(self):
        return PatronFT.invoke("configure", self)

    def new_brewers(self, brewers):  # pragma: no cover
        return PatronFT.invoke("new_brewers", self, brewers)

    def remove_brewer(self, brewer_id):  # pragma: no cover
        return PatronFT.invoke("remove_brewer", self, brewer_id)

    def reset(self):  # pragma: no cover
        return PatronFT.invoke("reset", self)

    def _handle_callback(self, brewer_id, data):  # pragma: no cover
        return PatronFT.invoke("_handle_callback", self, brewer_id, data)
