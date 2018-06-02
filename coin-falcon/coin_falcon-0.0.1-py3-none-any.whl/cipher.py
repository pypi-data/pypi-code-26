import hashlib
import hmac
import time

class Cipher():

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def sign(self, request):
        request.headers = self.headers(request.to_a())

    def headers(self, attrs):
        timestamp = str(int(time.time()))

        return {
            "CF-API-KEY": self.key,
            "CF-API-TIMESTAMP": timestamp,
            "CF-API-SIGNATURE": self.encode(timestamp, attrs)
        }

    def encode(self, timestamp, attrs):
        payload = self.build_payload(timestamp, attrs)
        print(">>>[PAYLOAD] {}".format(payload))

        message = bytes(payload, 'utf-8')
        secret = bytes(self.secret, 'utf-8')

        return hmac.new(secret, message, hashlib.sha256).hexdigest()

    def build_payload(self, timestamp, attrs):
        attrs = [attr for attr in attrs if attr is not None]

        return '|'.join([timestamp, *attrs])

    # def request_path(self, url):
    #     query = urllib.parse.urlparse(url).query
    #     if query == '':
    #         return urllib.parse.urlparse(url).path
    #     return urllib.parse.urlparse(url).path + '?' + query

    # def get_headers(self, method, request_path, body={}):
    #     timestamp = str(int(time.time()))

    #     if method == 'GET':
    #         payload = '|'.join([timestamp, method, request_path])
    #     else:
    #         payload = '|'.join([timestamp, method, request_path, json.dumps(body, separators=(',', ':'))])

    #     print(payload)
    #     message = bytes(payload, 'utf-8')
    #     secret = bytes(self.secret, 'utf-8')

    #     signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
    #     return {
    #         "CF-API-KEY": self.key,
    #         "CF-API-TIMESTAMP": timestamp,
    #         "CF-API-SIGNATURE": signature
    #     }
