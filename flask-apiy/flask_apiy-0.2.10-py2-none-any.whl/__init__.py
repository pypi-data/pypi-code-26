from commony import compose_decorator
from marshmallow import Schema

from .utils import parse_connection_string, api_result, request_data


class Apiy(object):
    def __init__(self, app=None, db=None, auto_bind=True):
        self.auto_bind = auto_bind
        if app and db:
            self.init_app(app, db)

    def init_app(self, app, db):
        self.app = app
        self.db = db

        if self.auto_bind:
            self.app.before_first_request(self._bind)

    def __call__(self, *args, **options):
        if not args:
            raise ValueError('args')

        rule = args[0]
        options.setdefault('methods', ['POST'])
        decorators = [self.app.route(rule, **options), api_result]

        for arg in args[1:]:
            if isinstance(arg, type) and issubclass(arg, Schema):
                decorators.append(request_data(arg))
            elif callable(arg):
                decorators.append(arg)
        return compose_decorator(*decorators)

    def _bind(self):
        self.db.bind(**parse_connection_string(self.app.config.get('DATABASE_URI')))
        self.db.generate_mapping()
