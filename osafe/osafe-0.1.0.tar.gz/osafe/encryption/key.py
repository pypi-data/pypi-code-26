from cached_property import cached_property
from osafe.utils import NoValueEnum

from .content import Content


class Key:
    class Label(NoValueEnum):
        PASSPHRASE = object()

    def __init__(self, label, content):
        self.label = label
        self.content = content

    @cached_property
    def encoded(self):
        return {
            'label': self.label.name,
            'content': self.content.encoded,
        }

    @classmethod
    def decode(cls, d):
        return cls(
            label=cls.Label[d['label']],
            content=Content.decode(d['content']),
        )
