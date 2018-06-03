from .base import HandlerBase
import pickle, hashlib
from pathlib import Path
import numpy as np


class NumPyHandler(HandlerBase):

    def understands(self, value):
        return type(value) is np.ndarray

    def quicksum(self, value):
        return self.checksum(value)

    def checksum(self, value):
        original = value.flags.writeable
        value.flags.writeable = False
        h = hash(value.data)
        value.flags.writeable = original
        m = hashlib.md5()
        m.update(str(h))
        return m.hexdigest()

    def serialize(self, value, handle):
        np.save(value)
        return {}

    def deserialize(self, metadata, handle):
        return np.load(handle)
