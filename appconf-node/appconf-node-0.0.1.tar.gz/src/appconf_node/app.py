# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from datetime import timedelta
from os.path import join

# 3rd party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# local imports
from appconf_node import PKG_DIR


app = Flask(__name__)
app.debug = True
db = SQLAlchemy()


def init_app():
    from . import routes
    # from .core.auth import jwt
    from .core.serialize import serialize       # pylint: disable: unused-import
    from .users.auth import jwt

    # import all models so the tables are created
    from .users import User
    from .nginx.models import Site


    global g_endpoints

    cfg = load_config(join(PKG_DIR, 'run/config.json'))
    app.config.update(cfg)

    jwt.init_app(app)
    db.init_app(app)
    db.create_all()
    routes.init_app(app)


def load_config(conf_path):
    try:
        app_cfg = json.load(open(conf_path))
    except json.decoder.JSONDecodeError as ex:
        raise RuntimeError("Failed to load config: {}".format(str(ex)))

    # Deserialize JSON data
    deserializers = {
        'JWT_EXPIRATION_DELTA': lambda x: timedelta(seconds=x)
    }

    for name, deserialize in deserializers.items():
        if name in app_cfg:
            app_cfg[name] = deserialize(app_cfg[name])

    # Apply defaults
    db_path = app_cfg.get('DB_PATH', 'db.sqlite')
    defaults = {
        'JWT_SECRET_KEY': app_cfg['SECRET_KEY'],
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///{}'.format(db_path),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_AUTH_URL_RULE': '/api/login',
        "NGINX_DIR": "/etc/nginx",
        "JWT_EXPIRATION_DELTA": timedelta(seconds=600),
        'CERT_DIR': '/etc/letsencrypt/live'
    }

    for name, value in defaults.items():
        # app_cfg[name] = value
        app_cfg.setdefault(name, value)

    return app_cfg
