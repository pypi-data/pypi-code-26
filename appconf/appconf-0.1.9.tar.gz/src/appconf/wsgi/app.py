# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from datetime import timedelta
from os.path import dirname, join

# 3rd party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.debug = True
db = SQLAlchemy()


def init_app():
    from .auth import jwt
    cfg = json.load(open(join(dirname(__file__), 'run/config.json')))

    converters ={
        'JWT_EXPIRATION_DELTA': lambda x: timedelta(seconds=x)
    }

    for name, converter in converters.items():
        if name in cfg:
            cfg[name] = converter(cfg[name])

    app.config.update(cfg)

    jwt.init_app(app)
    db.init_app(app)
    db.create_all()
