from Crypto.Cipher import AES
from cached_property import cached_property
from osafe.utils import NoValueEnum
import base64
import hashlib
import secrets


class Content:
    class CipherType(NoValueEnum):
        AES_128 = object()

    TRANSFORMATIONS = {
        CipherType.AES_128: AES,
    }

    MODES = {
        CipherType.AES_128: AES.MODE_CBC,
    }

    class DigestType(NoValueEnum):
        SHA_1 = object()

    DIGESTS = {
        DigestType.SHA_1: hashlib.sha1,
    }

    DEFAULT_CIPHER = CipherType.AES_128
    DEFAULT_DIGEST = DigestType.SHA_1

    def __init__(self, cipher_type, digest_type, iv, digest, content):
        self.cipher_type = cipher_type
        self.digest_type = digest_type
        self.iv = iv
        self.digest = digest
        self.content = content

    @classmethod
    def encrypt(cls, key, content):
        transformation = cls.TRANSFORMATIONS[cls.DEFAULT_CIPHER]
        iv = secrets.token_bytes(transformation.block_size)
        cipher = transformation.new(
            key=key[:transformation.block_size],
            mode=cls.MODES[cls.DEFAULT_CIPHER],
            IV=iv,
        )
        return cls(
            cipher_type=cls.DEFAULT_CIPHER,
            digest_type=cls.DEFAULT_DIGEST,
            iv=iv,
            digest=cls.DIGESTS[cls.DEFAULT_DIGEST](content).digest(),
            content=cipher.encrypt(cls._pkcs5_pad(content, transformation.block_size))
        )

    def decrypt(self, key):
        transformation = self.TRANSFORMATIONS[self.cipher_type]
        cipher = transformation.new(
            key=key[:transformation.block_size],
            mode=self.MODES[self.cipher_type],
            IV=self.iv,
        )
        content = self._pkcs5_unpad(cipher.decrypt(self.content))
        if self.digest != self.DIGESTS[self.digest_type](content).digest():
            return None
        return content

    @staticmethod
    def _pkcs5_pad(content, block_size):
        return content + (block_size - len(content) % block_size) * bytes((block_size - len(content) % block_size,))

    @staticmethod
    def _pkcs5_unpad(content):
        return content[0:-content[-1]]

    @cached_property
    def encoded(self):
        return {
            'cipherType': self.cipher_type.name,
            'digestType': self.digest_type.name,
            'iv': base64.b64encode(self.iv).decode('utf-8'),
            'digest': base64.b64encode(self.digest).decode('utf-8'),
            'content': base64.b64encode(self.content).decode('utf-8'),
        }

    @classmethod
    def decode(cls, d):
        return cls(
            cipher_type=cls.CipherType[d['cipherType']],
            digest_type=cls.DigestType[d['digestType']],
            iv=base64.b64decode(d['iv']),
            digest=base64.b64decode(d['digest']),
            content=base64.b64decode(d['content']),
        )
