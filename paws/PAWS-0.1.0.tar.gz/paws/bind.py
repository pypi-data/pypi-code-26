

class http:
    def __init__(self, handler, url, *, method='any', cors=None):
        self.url = url
        self.method = method
        self.handler = handler
        self.cors = cors

    class CORS:
        __slots__ = (origin, headers, allowCredentials,)

        def __init__(self, origin, headers=None, allowCredentials=False):
            self.origin = origin
            self.headers = headers or {}
            self.allowCredentials = allowCredentials

    def event(self):
        # Infer methods?
        ev = {
            'http': {
                'path': self.url,
                'method': self.method,
            },
        }
        if self.cors:
            ev['http']['cors'] = True

        return ev
