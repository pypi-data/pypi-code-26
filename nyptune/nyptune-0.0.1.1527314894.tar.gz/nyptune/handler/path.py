from .base import HandlerBase
from pathlib import Path
import os, hashlib, base64, pickle


class PathHandler(HandlerBase):

    def understands(self, value):
        try:
            print(value)
            if isinstance(value, Path):
                return True
            elif type(value) is str and len(value) < 200 and Path(str(value)).is_file():
                return True
            else:
                return False
        except:
            return False

    def quicksum(self, value):
        path = Path(str(value))
        stats = os.stat(path)
        return str(stats.st_size) + str(stats.st_mtime)

    def checksum(self, value):
        path = Path(str(value))
        with open(path, "rb") as file:
            m = hashlib.md5()
            block = b"whatever"
            while len(block) > 0:
                block = file.read(1 << 20)
                m.update(block)
        return m.hexdigest()

    def serialize(self, value, handle):
        path = Path(str(value))
        with open(path, "rb") as file:
            m = hashlib.md5()
            block = b"whatever"
            while len(block) > 0:
                block = file.read(1 << 20)
                handle.write(block)

        return {"original": base64.b64encode(pickle.dumps(value)).decode("ASCII")}

    def deserialize(self, metadata, handle):
        original = pickle.loads(base64.b64decode(metadata["original"]))
        path = Path(str(original))
        with open(path, "wb") as file:
            block = b"whatever"
            while len(block) > 0:
                block = handle.read(1 << 20)
                file.write(block)
        return original
