from flask import request
from flask_classy import FlaskView
from .exceptions import InvalidParameterException
from .exceptions import ParameterNotFoundException


class FlaskyView(FlaskView):

    def get_parameter(self, name, default=None, require=False, formatter=None):
        if request.args and name in request.args:
            value = request.args.get(name)
        elif request.json and name in request.json:
            value = request.json.get(name)
        elif request.form and name in request.form:
            value = request.form.get(name)
        elif not require:
            return default
        else:
            raise ParameterNotFoundException(name)

        if formatter and value:
            try:
                value = formatter(value)
            except:
                raise InvalidParameterException(name, value)

        return value
