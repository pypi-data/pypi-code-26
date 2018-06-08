import dectate


class CORSAction(dectate.Action):

    filter_convert = {
        'model': dectate.convert_dotted_name
    }
    app_class_arg = True

    def __init__(self, model, view_name=None,
                 allowed_origin=None,
                 allowed_headers=None,
                 expose_headers=None,
                 allow_credentials=None,
                 max_age=None):
        self.model = model
        self.view_name = view_name
        self.allowed_origin = allowed_origin
        self.allowed_headers = allowed_headers
        self.expose_headers = expose_headers
        self.allow_credentials = allow_credentials
        self.max_age = max_age

    def identifier(self, app_class):
        return str((app_class, self.model, self.view_name))

    def perform(self, obj, app_class):
        allowed_origin = self.allowed_origin
        if allowed_origin is not None:
            app_class.get_cors_allowed_origin.register(
                lambda self, model, request, requested_origin: allowed_origin,
                model=self.model, view_name=self.view_name)

        allowed_headers = self.allowed_headers
        if allowed_headers is not None:
            app_class.get_cors_allowed_headers.register(
                (lambda self, model, request,
                 requested_headers: allowed_headers),
                model=self.model, view_name=self.view_name
            )

        expose_headers = self.expose_headers
        if expose_headers is not None:
            app_class.get_cors_expose_headers.register(
                lambda self, model, request: expose_headers,
                model=self.model, view_name=self.view_name
            )

        allow_credentials = self.allow_credentials

        if allow_credentials is not None:
            app_class.get_cors_allow_credentials.register(
                lambda self, model, request: allow_credentials,
                model=self.model, view_name=self.view_name
            )

        max_age = self.max_age

        if max_age is not None:
            app_class.get_cors_max_age.register(
                lambda self, model, request: max_age,
                model=self.model, view_name=self.view_name
            )
