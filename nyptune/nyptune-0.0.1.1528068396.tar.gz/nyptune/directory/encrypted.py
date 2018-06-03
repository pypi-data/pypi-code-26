from .base import DirectoryBase
import base64, hashlib, os, io
from Crypto.Cipher import AES


class EncryptedDirectory(DirectoryBase):

    def __init__(self, inner, secret):
        self.inner = inner
        if inner.exists("_salt"):
            with inner.reader("_salt") as file:
                salt = file.read()
        else:
            salt = os.urandom(16)
            with inner.writer("_salt") as file:
                file.write(salt)
        self.key = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 100000)

    def glob(self, pattern):
        return self.inner.glob(pattern)

    def remove(self, name):
        return self.inner.remove(name)

    def exists(self, name):
        return self.inner.exists(name)

    def writer(self, name):
        return EncryptedWriter(self.inner.writer(name), self.key)

    def reader(self, name):
        return io.BufferedReader(EncryptedReader(self.inner.reader(name), self.key))


class EncryptedWriter(io.BufferedIOBase):

    def __init__(self, inner, key):
        self.cipher = AES.new(key, AES.MODE_EAX)
        self.inner = inner

    def write(self, content):
        ciphertext, tag = self.cipher.encrypt_and_digest(content)
        [
            inner.write(x)
            for x in (
                cipher.nonce,
                tag,
                len(ciphertext).to_bytes(8, byteorder="big"),
                ciphertext,
            )
        ]

    def close(self):
        return inner.close()


class EncryptedReader(io.BufferedIOBase):

    def __init__(self, inner, key):
        self.cipher = AES.new(key, AES.MODE_EAX)
        self.inner = inner

    def read(self, size=-1):
        assert size == -1, "Not wrapped in a BufferedReader"

        nonce = inner.read(16)
        if len(nonce) == 0:
            return nonce
        tag = inner.read(16)
        size = int.from_bytes(inner.read(8), "big")
        ciphertext = inner.read(size)
        return self.cypher.decrypt_and_verify(ciphertext, tag)

    def close(self):
        return inner.close()
