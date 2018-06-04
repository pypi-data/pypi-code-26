from decimal import Decimal
from functools import wraps
from json import loads, dumps, JSONEncoder
from urlparse import urlparse, parse_qsl

from flask import request
from werkzeug.exceptions import BadRequest, HTTPException


class ApifyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(ApifyEncoder, self).default(o)


def parse_connection_string(conn_str):
    uri = urlparse(conn_str)
    result = dict(provider='postgres' if uri.scheme == 'postgresql' else uri.scheme)

    if result['provider'] == 'sqlite':
        result.update(filename=uri.path[1:])
    elif result['provider'] in ('mysql', 'postgres'):
        result.update(host=uri.hostname,
                      port=uri.port,
                      user=uri.username,
                      password=uri.password,
                      database=uri.path[1:],
                      **dict(parse_qsl(uri.query)))
    elif result['provider'] == 'oracle':
        result.update(user=uri.username, password=uri.password,
                      dsn='{0}/{1}'.format(uri.hostname, uri.path[1:]))
    else:
        raise NotImplemented('provider `{}` not support'.format(result['provider']))
    return result


def request_data(schema):
    def decorator(func):
        @wraps(func)
        def decoration_function(*args, **kwargs):
            if request.method == "GET":
                data = request.args.to_dict(flat=False)
            else:
                data = request.get_data()
                if data:
                    try:
                        data = loads(data)
                    except:
                        raise BadRequest('required valid json request body')
                else:
                    data = {}

            clear_data, errors = schema().load(data)
            if errors or not clear_data:
                raise BadRequest({'errors': errors})
            return func(*args, request_data=clear_data, **kwargs)
        return decoration_function
    return decorator


def api_result(func):
    @wraps(func)
    def decoration_function(*args, **kwargs):
        try:
            rv = dumps(func(*args, **kwargs), cls=ApifyEncoder)
            return rv
        except HTTPException as http_except:
            return dumps(http_except.description, cls=ApifyEncoder), http_except.code
    return decoration_function
