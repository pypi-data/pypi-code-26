from tornado import web
import functools


def api_authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise web.HTTPError(401)
        method(self, *args, **kwargs)

    return wrapper


from .base import BaseHandler  # noqa
from .auth import AuthLoginHandler, AuthLogoutHandler  # noqa
from .token import TokenHandler  # noqa
from .user import UserHandler  # noqa
from .validate import ValidateHandler  # noqa
from .web import WebHandler  # noqa
