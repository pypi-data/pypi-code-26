import urllib
import json

class Request():

    def __init__(self, method, path, params):
        self.method = method
        if self.method == 'GET':
            self.full_path = self.encode_path_params(path, params)
            self.body = None
        else:
            self.full_path = path
            self.body = params

    def encode_path_params(self, path, params):
        if params == None or params == {}:
            return path
        else:
            return path + '?' + urllib.parse.urlencode(params)

    def to_a(self):
        if self.method == 'GET':
            return [self.method, self.full_path]
        else:
            return [self.method, self.full_path, json.dumps(self.body, separators=(',', ':'))]

