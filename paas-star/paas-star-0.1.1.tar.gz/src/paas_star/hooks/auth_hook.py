from apistar import Route

from ..components.session import Session


class AuthHook(object):

    def on_request(self, route: Route, session: Session):
        if getattr(route.handler, "need_login", False):
            assert session.user, "Login required!"


def auth(func):
    func.need_login = True
    return func


