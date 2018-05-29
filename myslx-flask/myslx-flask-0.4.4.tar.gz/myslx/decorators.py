from functools import wraps

from flask import g, abort

from myslx.utils import has_roles, redirect_to_login


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect_to_login()

        return f(*args, **kwargs)

    return decorated_function


def requires_roles(*roles):

    def wrapper(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):
            # this implies the user is authenticated
            if g.user is None:
                return redirect_to_login()

            if not has_roles(g.user['authorities'], roles):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return wrapper
