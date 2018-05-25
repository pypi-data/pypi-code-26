

class BaseExtension(object):
    extension_name = None
    app_attribute = None

    def __init__(self, app=None, app_attribute: str=None, *args, **kwargs):
        self.app = app
        self.app_attribute = app_attribute or self.app_attribute

        if app:
            self._register_extension(app, *args, **kwargs)
            self.init_app(app, *args, **kwargs)

    def _register_extension(self, app, *args, **kwargs):
        if not hasattr(app, 'extensions'):
            setattr(app, 'extensions', {})

        app.extensions[self.extension_name] = self

    def init_app(self, app, *args, **kwargs):
        setattr(app, self.app_attribute, self)

    def get_from_app_config(self, app, parameter, default=None):
        return getattr(app.config, parameter, default)

    async def init(self, loop):
        pass

    async def deinit(self, loop):
        pass
