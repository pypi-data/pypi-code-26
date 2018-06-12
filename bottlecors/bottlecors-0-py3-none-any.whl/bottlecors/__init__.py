import bottle


def wide_open_cors(app, allow_credentials=True):
    cors_string = 'Origin, Accept , Content-Type, X-Requested-With, X-CSRF-Token'
    CORS_HEADERS = {'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
                    'Access-Control-Allow-Headers': cors_string}
    if allow_credentials:
        CORS_HEADERS['Access-Control-Allow-Credentials'] = 'true'

    @app.hook('after_request')
    def add_cors_headers():
        origin = bottle.request.headers.get('Origin', '*')
        d = dict(CORS_HEADERS)
        d['Access-Control-Allow-Origin'] = origin
        bottle.response.headers.update(d)

    @app.route('/<url:re:.*>', method=['OPTIONS'])
    def verify_auth(url):
        return ''
    return app
