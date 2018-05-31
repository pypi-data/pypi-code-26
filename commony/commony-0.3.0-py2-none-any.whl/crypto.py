from base64 import urlsafe_b64encode
from hashlib import sha256, md5 as md5_
from hmac import HMAC


__all__ = ["encrypt", "decrypt", "hmac", "md5"]


def encrypt(password, plaintext):
    """对称加密解密，使用字符串密码加密指定内容"""
    return _s(_fernet(password).encrypt(_b(plaintext)))


def decrypt(password, ciphertext):
    """对称加密解密，使用字符串解密指定内容"""
    return _s(_fernet(password).decrypt(_b(ciphertext)))


def hmac(key, msg, digestmod=md5_):
    """生成消息认证码"""
    return HMAC(_b(key), _b(msg), digestmod).hexdigest()


def md5(msg):
    """生成 MD5 码"""
    return md5_(_b(msg)).hexdigest()


def _fernet(password):
    from cryptography.fernet import Fernet
    return Fernet(urlsafe_b64encode(sha256(_b(password)).digest()))


def _b(input):
    return input.encode() if isinstance(input, str) else input


def _s(output):
    return output.decode() if isinstance(output, (bytes, bytearray)) else output
