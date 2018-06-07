# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import join

# 3rd party imports
from flask import send_file
from tabulate import tabulate

# local imports
from appconf_node import PKG_DIR
from appconf_node.core.api import FlaskEndpoint


def init_app(app):
    # All REST resources should be imported here
    from .users.resource import UserResource
    from .nginx.resource import SiteResource

    FlaskEndpoint.init_app(
        app,
        resources=[
            ['/api/user/', UserResource, {'protected': True}],
            ['/api/site/', SiteResource, {'protected': True}]
        ],
    )

    # Catch-all route must be the last one defined
    app.add_url_rule('/', view_func=index)
    app.add_url_rule('/<path:path>', view_func=index)

    if app.debug:
        # Print URL config
        route_tab = [
            (r.endpoint, ', '.join(r.methods), r.rule)
            for r in app.url_map._rules
        ]
        print(tabulate(route_tab, headers=('Name', 'methods', 'URL')))


def index(path=None):
    return send_file(join(PKG_DIR, 'static/index.html'))
