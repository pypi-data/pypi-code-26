import uuid

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

def generate_state_random():
    return uuid.uuid4().hex

