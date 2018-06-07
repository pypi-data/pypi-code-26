# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
import time

# 3rd party imports
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from six import iteritems
from gunicorn.app.base import BaseApplication

# local imports
from appconf_node.core.config import ConfigLoader
from appconf_node.core.util import cfmt

app = None
db = SQLAlchemy()


def init_app(conf_path):
    # from .core.auth import jwt
    from .core.serialize import serialize       # pylint: disable: unused-import
    from .users.auth import jwt

    init_t0 = time.time()

    global app
    app = Flask(__name__)
    app.debug = True

    ConfigLoader(conf_path).init_app(app)

    app.app_context().push()

    # import all models so the tables are created
    from .users import User
    from .nginx.models import Site

    db.init_app(app)

    # only import routes after the app is created
    from . import routes

    routes.init_app(app)

    # Initialize the auth system
    jwt.init_app(app)

    # Create DB tables after everything is imported
    db.create_all()

    init_time = int((time.time() - init_t0) * 1000)
    print(cfmt("^32App initialized in ^35{} ms^0", init_time))
    return app


class GunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def _iter_cfg_options(self):
        for key, value in iteritems(self.options):
            if key in self.cfg.settings and value is not None:
                yield key, value

    def load_config(self):
        for key, value in self._iter_cfg_options():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
