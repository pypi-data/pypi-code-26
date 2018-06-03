from .base import HandlerBase
from pathlib import Path
import os, hashlib, base64, pickle
from nyptune.util import Download


class DownloadHandler(HandlerBase):

    def understands(self, value):
        return isinstance(value, Download)

    def quicksum(self, value):
        return value.url

    def checksum(self, value):
        path = value.path
        with open(path, "rb") as file:
            m = hashlib.md5()
            block = b"whatever"
            while len(block) > 0:
                block = file.read(1 << 20)
                m.update(block)
        return m.hexdigest()

    def serialize(self, value, handle):
        with open(value.path, "rb") as file:
            m = hashlib.md5()
            block = b"whatever"
            while len(block) > 0:
                block = file.read(1 << 20)
                handle.write(block)

        return {"url": value.url, "path": str(value.path)}

    def deserialize(self, metadata, handle):
        original = Download(metadata["url"], metadata["path"])
        with open(original.path, "wb") as file:
            block = b"whatever"
            while len(block) > 0:
                block = handle.read(1 << 20)
                file.write(block)
        return original
