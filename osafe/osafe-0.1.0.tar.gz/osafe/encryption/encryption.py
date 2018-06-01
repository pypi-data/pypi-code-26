import hashlib
import secrets

from .content import Content
from .key import Key
from .message import Message


class Encryption:
    def __init__(self, passphrase):
        self.key = hashlib.sha512(passphrase.encode('utf-8')).digest()
        self.original = None
        self.base_key = None

    def encrypt(self, content):
        if not self.base_key:
            self.base_key = secrets.token_bytes(64)
        self.original = Message(
            keys=(self.original and self.original.keys) or [
                Key(
                    label=Key.Label.PASSPHRASE,
                    content=Content.encrypt(
                        key=self.key,
                        content=self.base_key
                    )
                )
            ],
            content=Content.encrypt(
                key=self.base_key,
                content=content.encode('utf-8')
            )
        )
        return self.original

    def add_key(self):
        self.original = Message(
            keys=self.original.keys + [
                Key(
                    label=Key.Label.PASSPHRASE,
                    content=Content.encrypt(
                        key=self.key,
                        content=self.base_key
                    )
                )
            ],
            content=self.original.content
        )
        return self.original

    def decrypt(self, message):
        for key in message.keys:
            if key.label != Key.Label.PASSPHRASE:
                continue
            self.base_key = key.content.decrypt(self.key)
            if self.base_key:
                break
        if not self.base_key:
            return None

        content = message.content.decrypt(self.base_key).decode('utf-8')
        self.original = message
        return content
