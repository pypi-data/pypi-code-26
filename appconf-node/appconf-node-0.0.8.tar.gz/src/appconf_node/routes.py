# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import join

# 3rd party imports
from flask import send_file

# local imports
from appconf_node import PKG_DIR
from appconf_node.core.api import api_route, FlaskEndpoint


def init_app(app):
    # All REST resources should be imported here
    from .users.resource import UserResource
    from .nginx.resource import SiteResource

    # All routes should be imported here
    from .nginx import routes as nginx_routes
    from .users import routes as user_routes

    FlaskEndpoint.init_app(app, '/api', [
        ['user/', UserResource, {'protected': True}],
        ['site/', SiteResource, {'protected': True}]
    ])

    urlconf = [
        ('/api/login/', user_routes.login),
        ('/api/nginx/reload/', nginx_routes.reload_nginx),
        ('/api/site/<site_id>/config/', nginx_routes.site_config),
        ('/api/site/<site_id>/start/', nginx_routes.site_start),
        ('/api/site/<site_id>/stop/', nginx_routes.site_stop),
    ]

    for url, route in urlconf:
        meta = api_route.get_meta(route)
        app.add_url_rule(url, view_func=route, **meta)

    app.add_url_rule('/', view_func=index)
    app.add_url_rule('/<path:path>', view_func=index)


def index(path=None):
    return send_file(join(PKG_DIR, 'static/index.html'))
