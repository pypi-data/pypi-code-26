import json
import inspect
from flask import Flask
from flask import request
from flask import jsonify
from . import log
from .view import FlaskyView
from .exceptions import get_traceback
from .exceptions import FlaskyException
from .exceptions import InvalidParameterException
from .exceptions import ParameterNotFoundException


class FlaskyServer:

    def __init__(self, name="Flasky"):
        self.app = Flask(name)
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)
        self.set_error_handler(404, self._not_found_handler)
        self.set_error_handler(ParameterNotFoundException, self._parameter_error_handler)
        self.set_error_handler(InvalidParameterException, self._parameter_error_handler)
        self.set_error_handler(Exception, self._default_error_handler)

    def _before_request(self):
        try:
            data = None
            if request.method.upper() in ["POST", "PUT", "PATCH"]:
                if request.data and len(request.data) > 0:
                    data = request.data
                elif request.form:
                    data = json.dumps(request.form)
            elif request.method.upper() in ["GET", "DELETE"]:
                data = json.dumps(request.args)

            data = data if data and len(data) > 0 else "N/A"

            log.http.info("Receive Request - Method=[%s] - Url=[%s]" % (request.method, self._get_current_url()))
            log.http.debug("Receive Data - Method=[%s] - Url=[%s] - Data=[%s]" % (request.method, self._get_current_url(), data))
        except Exception as ex:
            log.http.error(get_traceback(ex))

    def _after_request(self, response):
        data = response.data if len(response.data) <= 100 else response.data[0:100] + b"..."
        log.http.info("Send Response - Method=[%s] - Url=[%s] - Status=[%s]" % (request.method, self._get_current_url(), response.status_code))
        log.http.debug("Send Data - Method=[%s] - Url=[%s] - Data=[%s]" % (request.method, self._get_current_url(), data))
        return response

    def _get_current_url(self):
        return request.path if len(request.query_string) == 0 else request.path + "?" + request.query_string.decode("utf-8")

    def _not_found_handler(self, ex):
        return jsonify(error=str(ex)), 404

    def _parameter_error_handler(self, ex):
        log.http.error(get_traceback(ex))
        return jsonify(error=str(ex)), 400

    def _default_error_handler(self, ex):
        log.http.error(get_traceback(ex))
        return jsonify(error=str(ex)), 500

    def set_error_handler(self, code_or_exception, func):
        self.app.errorhandler(code_or_exception)(func)

    def register_view(self, cls):
        if issubclass(cls, FlaskyView) and hasattr(cls, "register"):
            obj = cls()
            getattr(obj, "register")(app=self.app, route_base="/")

            for name, value in cls.__dict__.items():
                func = getattr(obj, name)
                if inspect.ismethod(func) and hasattr(func, "_rule_cache"):
                    for rule_name, rule_value in func._rule_cache.items():
                        for route in rule_value:
                            route_prefix = getattr(cls, "route_prefix") if hasattr(cls, "route_prefix") else None
                            url = route_prefix.rstrip("/") + "/" + route[0].lstrip("/") if route_prefix is not None else route[0]
                            methods = route[1]["methods"]
                            log.flasky.info("Register View - Class=[%s] - Url=[%s] - Methods=%s" % (cls.__name__, url, methods))
        else:
            raise FlaskyException("Your view isn't a FlaskyView")

    def run(self, host=None, port=None):
        log.flasky.info("Starting server at '%s:%s'" % (host, port))
        self.app.run(host=host, port=port)
