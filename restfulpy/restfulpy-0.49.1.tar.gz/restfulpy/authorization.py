
import functools

from nanohttp import context, HttpUnauthorized


def authorize(*roles):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            identity = context.identity

            if not identity:
                raise HttpUnauthorized()

            identity.assert_roles(*roles)

            return func(*args, **kwargs)

        return wrapper

    if roles and callable(roles[0]):
        f = roles[0]
        roles = []
        return decorator(f)
    else:
        return decorator
