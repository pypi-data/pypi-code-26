from .base import HandlerBase
import pickle, hashlib
from pathlib import Path


class PickleHandler(HandlerBase):

    def understands(self, value):
        return True

    def quicksum(self, value):
        try:
            return str(hash(value))
        except:
            return None

    def checksum(self, value):
        block = pickle.dumps(value)
        path = Path(str(value))
        m = hashlib.md5()
        m.update(block)
        return m.hexdigest()

    def serialize(self, value, handle):
        pickle.dump(value, handle)
        return {}

    def deserialize(self, metadata, handle):
        return pickle.load(handle)
