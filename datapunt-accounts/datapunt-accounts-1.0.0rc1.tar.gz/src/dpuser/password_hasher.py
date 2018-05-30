"""
Secure password hashing using the PBKDF2 algorithm (recommended)

Configured to use PBKDF2 + HMAC + SHA256.
The result is a 64 byte binary string.  Iterations may be changed
safely but you must rename the algorithm if you change SHA256.
"""

import hashlib
import base64
from secrets import token_urlsafe

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 30000
DIGEST = hashlib.sha256


def _force_bytes(s):
    """Forces strings to bytes."""
    if isinstance(s, bytes):
        return s
    return s.encode('utf-8')


def pbkdf2(password, salt, iterations, dklen=0):
    """
    Implements PBKDF2 with the same API as Django's existing
    implementation, using the stdlib.

    This is used in Python 2.7.8+ and 3.4+.
    """
    if not dklen:
        dklen = None
    password = _force_bytes(password)
    salt = _force_bytes(salt)
    return hashlib.pbkdf2_hmac(DIGEST().name, password, salt, iterations, dklen)


def encode(password, salt=None, iterations=ITERATIONS):
    """Encodes passwords."""
    if salt is None:
        salt = token_urlsafe(12)
    assert password is not None
    assert salt and '$' not in salt
    thing = pbkdf2(password, salt, iterations)
    thing = base64.b64encode(thing).decode('ascii').strip()
    return "%s$%d$%s$%s" % (ALGORITHM, iterations, salt, thing)


def _constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    if isinstance(val1, bytes) and isinstance(val2, bytes):
        for x, y in zip(val1, val2):
            result |= x ^ y
    else:
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
    return result == 0


def verify(password, encoded):
    """Verifies."""
    algorithm, iterations, salt, _ = encoded.split('$', 3)
    assert algorithm == algorithm
    encoded_2 = encode(password, salt, int(iterations))
    return _constant_time_compare(encoded, encoded_2)
