import json
from aoet import logger

def parse_headers(data, is_request=False):
    headers = {}
    for h in data[1:]:
        t = h.split(b':', 1)
        headers[t[0].decode('utf-8').lower()] = t[1].decode('utf-8')
    if not is_request:
        status = data[0].split(b' ', 1)[1]
        return status.decode('utf-8'), headers
    else:
        first_line = data[0].split(b' ')
        return first_line[0].decode('utf-8'), first_line[1].decode('utf-8'), headers


def parse_body(headers, data):
    body = None
    if 'content-type' in headers:
        if 'json' in headers['content-type']:
            body = json.loads(data.decode('utf-8'))
        else:
            logger.warn('Unknown content-type: ' + headers['content-type'])
    return body


class HttpRequest:
    @staticmethod
    def from_socket(ind, data):
        return HttpRequest(ind, data)

    @staticmethod
    def from_json(j):
        return HttpRequest(j['id'], None, j['method'], j['path'], j['headers'], j['body'])

    def __init__(self, ind, data, method=None, path=None, headers=None, body=None):
        self._ind = ind
        self._data_bytes = None
        self._remaining_data = 0
        if data is None:
            self._method, self._path, self._headers, self._body = method, path, headers, body
        else:
            self._method, self._path, self._headers, self._body = self._parse_request(data)

    def to_dict(self):
        return {'id': self.ind, 'method': self._method, 'path': self._path, 'headers': self._headers, 'body': self._body}

    def __str__(self):
        return str(self.to_dict())

    def _parse_request(self, data):
        parts = data.split(b'\r\n\r\n', 1)

        method, path, headers = parse_headers(parts[0].split(b'\r\n'), is_request=True)

        body = None

        if 'content-length' in headers:
            self._remaining_data = int(headers['content-length']) - len(parts[1])
            if self._remaining_data <= 0:
                body = parse_body(headers, parts[1])
            else:
                self._data_bytes = parts[1]
        else:
            body = parse_body(headers, parts[1])
            self._remaining_data = 0

        return method, path, headers, body

    def append_data(self, data):
        self._data_bytes += data
        self._remaining_data -= len(data)
        if self._remaining_data <= 0:
            self._body = parse_body(self._headers, self._data_bytes)
            self._data_bytes = None

    @property
    def remaining_bytes(self):
        return self._remaining_data

    @property
    def ind(self):
        return self._ind

    @property
    def method(self):
        return self._method

    @property
    def path(self):
        return self._path


class HttpResponse:
    @staticmethod
    def from_socket(ind, data):
        return HttpResponse(ind, data)

    @staticmethod
    def from_json(j):
        return HttpResponse(j['id'], None, j['status'], j['headers'], j['body'])

    @staticmethod
    def timeout(id):
        return HttpResponse(id, None, 504)

    def __init__(self, ind, data, status=None, headers=None, body=None):
        self._ind = ind
        self._data_bytes = None
        self._remaining_data = 0
        if data is None:
            self._status, self._headers, self._body = status, headers, body
        else:
            self._status, self._headers, self._body = self.parse_response(data)

    def append_data(self, data):
        self._data_bytes += data
        self._remaining_data -= len(data)
        if self._remaining_data <= 0:
            self._body = parse_body(self._headers, self._data_bytes)
            self._data_bytes = None

    def to_dict(self):
        return {'id': self.ind, 'status': self.status, 'headers': self.headers, 'body': self.body}

    def __str__(self):
        return str(self.to_dict())

    def parse_response(self, data):
        parts = data.split(b'\r\n\r\n', 1)
        status, headers = parse_headers(parts[0].split(b'\r\n'))
        body = None
        if 'content-length' in headers:
            self._remaining_data = int(headers['content-length']) - len(parts[1])
            if self._remaining_data <= 0:
                body = parse_body(headers, parts[1])
            else:
                self._data_bytes = parts[1]
        else:
            body = parse_body(headers, parts[1])
            self._remaining_data = 0
        return status, headers, body

    @property
    def ind(self):
        return self._ind

    @property
    def status(self):
        return self._status

    @property
    def headers(self):
        return self._headers

    @property
    def body(self):
        return self._body

    @property
    def remaining_bytes(self):
        return self._remaining_data
