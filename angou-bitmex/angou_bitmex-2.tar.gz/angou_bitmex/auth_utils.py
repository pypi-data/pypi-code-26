import time
import hmac
import hashlib


def generate_nonce():
    return int(round(time.time() * 1000))


def generate_signature(secret, verb, path, nonce, data):
    if isinstance(data, (bytes, bytearray)):
        data = data.decode('utf8')
    message = verb + path + str(nonce) + data
    signature = hmac.new(
        bytes(secret, 'utf8'),
        bytes(message, 'utf8'),
        digestmod=hashlib.sha256)
    return signature.hexdigest()
