# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from os.path import abspath, dirname, join, normpath

# 3rd party imports
from jinja2 import Environment, PackageLoader, select_autoescape


WEBAPP_DIR = normpath(abspath(join(dirname(__file__), '..')))
jinja = Environment(
    loader=PackageLoader('appconf.wsgi', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def json_response(code, data, headers=None):
    headers = dict(headers or {})
    headers['Content-Type'] = 'application/json'

    return json.dumps(data), code, headers
