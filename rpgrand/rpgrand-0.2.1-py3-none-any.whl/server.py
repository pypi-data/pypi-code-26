from flask import Flask, jsonify, make_response, request
from flask.json import JSONEncoder

from functools import update_wrapper

from .config_map import ConfigMap
from .categories import Category

config = "examples/human_male.yml"

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

def crossdomain(origin='*'):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route("/")
@crossdomain()
def main():
    cm = ConfigMap(config)
    c = Category.create(cm)
    return jsonify(c.items)


@app.route("/config-maps/", methods=["GET"])
@app.route("/config-maps/<config>", methods=["GET"])
@crossdomain()
def config_map(config=None):
    import os
    if request.method == 'GET':
        if config:
            c = os.path.join('categories', config)
            cm = ConfigMap(c)
            return jsonify(cm.config)
        else:
            d = os.listdir('./categories')
            return jsonify(d)
