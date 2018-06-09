import requests
import json

from .request import Request
from .cipher import Cipher

class Connection():

    def __init__(self, key, secret, endpoint):
        self.cipher = Cipher(key, secret)
        self.endpoint = endpoint

    def get(self, path, params = {}):
        return self.request('GET', path, params)

    def post(self, path, params):
        return self.request('POST', path, params)

    def delete(self, path, params = {}):
        return self.request('DELETE', path, params)

    def api(self, path):
        return "/api/v1/{}".format(path)

    def request(self, method, path, params):
        request = Request(method, self.api(path), params)
        self.cipher.sign(request)
        url = self.url_for(request.full_path)
        if method == 'GET':
            return requests.get(url, headers=request.headers).json()
        elif method == 'POST':
            return requests.post(url, headers=request.headers, data=request.body).json()
        elif method == 'DELETE':
            return requests.delete(url, headers=request.headers).json()

    def url_for(self, path):
        return self.endpoint + path

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

    # def create_order(self, body):
    #     url = self.endpoint + "/user/orders"
    #     headers = self.get_headers('POST', urllib.parse.urlparse(url).path, body)
    #     return requests.post(url, headers=headers, data=body).json()

    # def cancel_order(self, id):
    #     url = self.endpoint + "/user/orders/{}".format(id)
    #     print(url)
    #     headers = self.get_headers('DELETE', urllib.parse.urlparse(url).path, {})
    #     return requests.delete(url, headers=headers).json()

    # def my_orders(self, params):
    #     path = 'user/orders'
    #     # url = self.endpoint + "/user/orders"
    #     # headers = self.get_headers('GET', urllib.parse.urlparse(url).path)
    #     # return requests.get(url, headers=headers).json()
    #     return conn.get(path, params)
