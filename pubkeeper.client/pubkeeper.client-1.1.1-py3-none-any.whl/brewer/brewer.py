"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.function_table import FunctionTable
from pubkeeper.topic import Topic
from tornado import ioloop
from uuid import uuid4

__all__ = ['Brewer']
BrewerFT = FunctionTable()


class Brewer(Topic):
    def __init__(self, topic, brewer_id=None, io_loop=None, **kwargs):
        super().__init__(topic)

        self.brewer_id = brewer_id or uuid4().hex
        self._brewing = {}
        self._kwargs = kwargs

        if io_loop is None:
            self._io_loop = ioloop.IOLoop.current()
        else:
            self._io_loop = io_loop

    def configure(self):
        return BrewerFT.invoke("configure", self)

    def get_config(self):  # pragma: no cover
        return BrewerFT.invoke("get_config", self)

    def new_patrons(self, patrons):  # pragma: no cover
        return BrewerFT.invoke("new_patrons", self, patrons)

    def remove_patron(self, patron_id):  # pragma: no cover
        return BrewerFT.invoke("remove_patron", self, patron_id)

    def reset(self):  # pragma: no cover
        return BrewerFT.invoke("reset", self)

    def brew(self, data):  # pragma: no cover
        return BrewerFT.invoke("brew", self, data)
