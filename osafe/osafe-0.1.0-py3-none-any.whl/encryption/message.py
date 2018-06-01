from cached_property import cached_property
import json

from .content import Content
from .key import Key


class Message:
    def __init__(self, keys, content):
        self.keys = keys
        self.content = content

    @cached_property
    def encoded(self):
        return json.dumps({
            'keys': [key.encoded for key in self.keys],
            'content': self.content.encoded,
        }).encode('utf-8')

    @classmethod
    def decode(cls, json_bytes):
        d = json.loads(json_bytes)
        return cls(
            keys=[Key.decode(key) for key in d['keys']],
            content=Content.decode(d['content']),
        )
