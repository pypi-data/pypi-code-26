import hmac
import hashlib
import time


def generate_nonce():
    return int(time.time() * 1000000)


def generate_signature(secret, payload):
    if not isinstance(payload, (bytes, bytearray)):
        payload = payload.encode('utf8')
    return hmac.new(secret.encode('utf8'), payload, hashlib.sha512).hexdigest()
