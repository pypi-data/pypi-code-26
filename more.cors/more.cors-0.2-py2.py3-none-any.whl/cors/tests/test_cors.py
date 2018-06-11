from webtest import TestApp as Client
from webob.exc import HTTPUnauthorized
import morepath
from more.cors import CORSApp


class App(CORSApp):
    pass


class Object(object):
    pass


class FailedObject(object):
    pass


class UnauthorizedObject(object):
    pass


class Root(object):
    pass


@App.path(path='/', model=Root)
def get_root(request):
    return Root()


@App.path(path='obj', model=Object)
def get_object(request):
    return Object()


@App.path(path='failedobj', model=FailedObject)
def get_failed_object(request):
    raise Exception()


@App.path(path='unauthorized', model=UnauthorizedObject)
def get_unauthorized_object(request):
    raise HTTPUnauthorized


@App.json(model=Root)
def view(context, request):
    return {'view': 'index'}


@App.json(model=Root, request_method='POST')
def post_view(context, request):
    return {'view': 'index-post'}


@App.json(model=Root, name='view2')
def view2(context, request):
    return {'view': 'view2'}


@App.json(model=Root, name='view2', request_method='POST')
def post_view2(context, request):
    return {'view': 'view2-post'}


App.cors(
    model=Root,
    view_name='view2',
    allowed_headers=['Cache-Control'],
    expose_headers=['Cookie'],
    allowed_origin='http://localhost.localdomain',
    allow_credentials=True,
    max_age=10
)


def get_client(app):
    class Tapp(app):
        pass
    morepath.autoscan()
    morepath.commit(Tapp)
    c = Client(Tapp())
    return c


def test_cors_preflight():
    c = get_client(App)

    r = c.options('/', headers={'Origin': 'http://hello.world.com/'})

    assert r.headers.get(
        'Access-Control-Allow-Methods').split(',') == ['OPTIONS',
                                                       'GET',
                                                       'POST']
    assert r.headers.get('Access-Control-Allow-Origin') == '*'
    assert r.headers.get(
        'Access-Control-Allow-Headers').split(',') == ['Content-Type',
                                                       'Authorization']
    assert r.headers.get(
        'Access-Control-Expose-Headers').split(',') == ['Content-Type',
                                                        'Authorization']

    assert r.headers.get('Access-Control-Allow-Credentials') is None
    assert r.headers.get('Access-Control-Max-Age') == '60'


def test_cors_override():
    c = get_client(App)
    r = c.options('/view2', headers={'Origin': 'http://hello.world.com/'})

    assert r.headers.get(
        'Access-Control-Allow-Methods').split(',') == [
            'OPTIONS', 'GET', 'POST']
    assert r.headers.get(
        'Access-Control-Allow-Origin') == 'http://localhost.localdomain'
    assert r.headers.get(
        'Access-Control-Allow-Headers').split(',') == ['Cache-Control']
    assert r.headers.get(
        'Access-Control-Expose-Headers').split(',') == ['Cookie']

    assert r.headers.get('Access-Control-Allow-Credentials') == 'true'
    assert r.headers.get('Access-Control-Max-Age') == '10'


def test_cors_non_preflight():
    c = get_client(App)

    r = c.get('/', headers={'Origin': 'http://hello.world.com/'})

    assert r.headers.get('Access-Control-Allow-Origin') == '*'
    assert r.headers.get(
        'Access-Control-Expose-Headers').split(',') == ['Content-Type',
                                                        'Authorization']

    assert r.headers.get('Access-Control-Allow-Credentials') is None
    assert r.headers.get('Access-Control-Max-Age') is None


def test_cors_unauthorized_preflight():
    c = get_client(App)

    r = c.options('/unauthorized')

    assert r.headers.get(
        'Access-Control-Allow-Methods').split(',') \
        == ['OPTIONS'] + c.app.settings.cors.allowed_verbs


def test_cors_no_allowed_verbs():
    @App.setting(section='cors', name='allowed_verbs')
    def get_allowed_verbs():
        return []

    c = get_client(App)

    c.options(
        '/',
        headers={'Origin': 'http://hello.world.com/'},
        status=404
    )


def test_cors_failed_view():

    c = get_client(App)

    r = c.options('/failedobj', expect_errors=True)

    assert r.status_code == 404
