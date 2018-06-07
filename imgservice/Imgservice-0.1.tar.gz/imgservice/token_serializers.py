import base64
import json

from itsdangerous import URLSafeSerializer


class PlainJsonTokenSerializer:

    def load(self, token):
        return json.loads(
            base64.urlsafe_b64decode(token.encode()).decode())

    def dump(self, token):
        return base64.urlsafe_b64encode(
            json.dumps(token, separators=(',', ':')).encode()).decode()


class JsonHmacTokenSerializer:

    def __init__(self, shared_key):
        self.shared_key = shared_key
        self._serializer = URLSafeSerializer(shared_key)

    def load(self, token):
        return self._serializer.loads(token)

    def dump(self, token):
        return self._serializer.dumps(token)
