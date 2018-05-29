import hashlib
import random
import uuid


def uuidv4(*args):
    """Generates UUID v4"""
    return str(uuid.uuid4())


def md5(*args):
    """Generates MD5 based on the provided string or a random int"""
    value = ""
    if len(args) > 0:
        value = args[0]
    if value == "":
        value = str(random.getrandbits(128))
    return hashlib.md5(value.encode('utf-8')).hexdigest()


def sha1(*args):
    """Generates SH1 based on the provided string or a random int"""
    value = ""
    if len(args) > 0:
        value = args[0]
    if value == "":
        value = str(random.getrandbits(128))
    return hashlib.sha1(value.encode('utf-8')).hexdigest()


def sha256(*args):
    """Generates SHA256 based on the provided string or a random int"""
    value = ""
    if len(args) > 0:
        value = args[0]
    if value == "":
        value = str(random.getrandbits(256))
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def sha512(*args):
    """Generates SHA512 based on the provided string or random int"""
    value = ""
    if len(args) > 0:
        value = args[0]
    if value == "":
        value = str(random.getrandbits(512))
    return hashlib.sha512(value.encode('utf-8')).hexdigest()