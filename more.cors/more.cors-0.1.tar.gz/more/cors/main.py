import morepath
from morepath.publish import resolve_model, get_view_name
import dectate
import reg
from . import action


class App(morepath.App):

    _cors = dectate.directive(action.CORSAction)

    @classmethod
    def cors(cls, *args, **kwargs):
        cls._cors(*args, **kwargs)(None)

    @reg.dispatch_method(
        reg.match_instance('model'),
        reg.match_key('view_name',
                      lambda self, model, request,
                      requested_origin: request.view_name))
    def get_cors_allowed_origin(self, model, request, requested_origin):
        return self.settings.cors.allowed_origin

    @reg.dispatch_method(
        reg.match_instance('model'),
        reg.match_key('view_name',
                      lambda self, model, request,
                      requested_method: request.view_name))
    def get_cors_allowed_methods(self, model, request, requested_method):
        res = []
        for m in self.settings.cors.allowed_verbs:
            f = self.get_view.by_predicates(
                model=model.__class__, name=request.view_name,
                request_method=m)
            if f and f.component:
                res.append(m)
        return res

    @reg.dispatch_method(
        reg.match_instance('model'),
        reg.match_key('view_name',
                      lambda self, model, request,
                      requested_headers: request.view_name))
    def get_cors_allowed_headers(self, model, request, requested_headers):
        return self.settings.cors.allowed_headers

    @reg.dispatch_method(
        reg.match_instance('model'),
        reg.match_key('view_name',
                      lambda self, model, request: request.view_name))
    def get_cors_expose_headers(self, model, request):
        return self.settings.cors.expose_headers

    @reg.dispatch_method(
        reg.match_instance('model'),
        reg.match_key('view_name',
                      lambda self, model, request: request.view_name))
    def get_cors_allow_credentials(self, model, request):
        return self.settings.cors.allow_credentials

    @reg.dispatch_method(
        reg.match_instance('model'),
        reg.match_key('view_name',
                      lambda self, model, request: request.view_name))
    def get_cors_max_age(self, model, request):
        return self.settings.cors.max_age


CORSApp = App


@App.setting_section(section='cors')
def cors_settings():
    return {
        'allowed_verbs': ['GET', 'PUT', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
        'allowed_origin': '*',
        'expose_headers': ['Content-Type', 'Authorization'],
        'allowed_headers': ['Content-Type', 'Authorization'],
        'max_age': 60,
        'allow_credentials': False
    }


@App.tween_factory(over=morepath.EXCVIEW)
def cors_tween(app, handler):
    def cors_handler(request):
        preflight = request.method == 'OPTIONS'
        if preflight:
            response = request.ResponseClass()
        else:
            response = handler(request)

        try:
            context = resolve_model(request) or app
        except Exception:
            context = app

        _marker = []
        if getattr(request, 'view_name', _marker) is _marker:
            request.view_name = get_view_name(request.unconsumed)

        # Access-Control-Allow-Methods
        requested_method = request.headers.get('Access-Control-Request-Method')

        if preflight:
            allowed_methods = app.get_cors_allowed_methods(
                context, request, requested_method)
            if not allowed_methods:
                return request.ResponseClass(status_code=404)
            response.headers.add('Access-Control-Allow-Methods',
                                 ','.join(['OPTIONS'] + allowed_methods))

        # Access-Control-Allow-Headers
        requested_headers = request.headers.get(
            'Access-Control-Request-Headers')

        if preflight:
            allowed_headers = app.get_cors_allowed_headers(
                context, request, requested_headers)
            response.headers.add(
                'Access-Control-Allow-Headers', ','.join(allowed_headers))

        # Access-Control-Allow-Origin
        requested_origin = request.headers.get('Origin')

        if requested_origin or preflight:
            allowed_origin = app.get_cors_allowed_origin(
                context, request, requested_origin)
            response.headers.add('Access-Control-Allow-Origin', allowed_origin)
            if allowed_origin and allowed_origin != '*':
                response.headers.add('Vary', 'Origin')

        # Access-Control-Expose-Headers
        exposed_headers = app.get_cors_expose_headers(context, request)
        response.headers.add('Access-Control-Expose-Headers',
                             ','.join(exposed_headers))

        # Access-Control-Allow-Credentials
        allow_credentials = app.get_cors_allow_credentials(context, request)
        if allow_credentials is True:
            response.headers.add('Access-Control-Allow-Credentials', 'true')

        if preflight:
            max_age = app.get_cors_max_age(context, request)
            response.headers.add('Access-Control-Max-Age',
                                 str(max_age))

        return response
    return cors_handler
