import bottle


def __cors_dict(origin=None):
    origin = '*' if origin is None else origin
    cors_string = 'Origin, Accept , Content-Type, X-Requested-With, X-CSRF-Token'
    CORS_HEADERS = {'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
                    'Access-Control-Allow-Headers': cors_string,
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Origin': origin}
    return CORS_HEADERS


def abort(code=500, text='Unknown Error.'):
    """ Aborts execution and causes a HTTP error. """
    origin = bottle.request.headers.get('Origin')
    d = __cors_dict(origin)
    raise bottle.HTTPError(code, text, **d)


def wide_open_cors(app, allow_credentials=True):
    @app.hook('after_request')
    def add_cors_headers():
        origin = bottle.request.headers.get('Origin')
        d = __cors_dict(origin)
        bottle.response.headers.update(d)

    @app.route('/<url:re:.*>', method=['OPTIONS'])
    def verify_auth(url):
        return ''
    return app
