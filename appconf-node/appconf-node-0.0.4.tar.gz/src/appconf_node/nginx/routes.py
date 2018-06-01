# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from flask import request
from serafin import serialize

# local imports
from appconf_node.app import db
from appconf_node.core.api import api_route, json_response
from appconf_node.users.auth import jwt
from .models import Site
from . import util


@api_route(methods=['get'])
@jwt.authenticate()
def site_config(site_id):
    site = Site.query.get(site_id)

    if site is None:
        return json_response(404, {
            'detail': 'Site #{} not found'.format(site_id)
        })

    return site.config


@api_route(methods=['post'])
@jwt.authenticate()
def site_start(site_id):
    site = Site.query.get(site_id)

    if site is None:
        return json_response(404, {
            'detail': 'Site #{} not found'.format(site_id)
        })

    site.start()

    if not util.reload_nginx():
        return json_response(400, {
            'detail': "nginx is not running"
        })

    return json_response(200, serialize(site))


@api_route(methods=['post'])
@jwt.authenticate()
def site_stop(site_id):
    site = Site.query.get(site_id)

    if site is None:
        return json_response(404, {
            'detail': 'Site #{} not found'.format(site_id)
        })

    site.stop()

    if not util.reload_nginx():
        return json_response(400, {
            'detail': "nginx is not running"
        })

    return json_response(200, serialize(site))


@api_route(methods=['post'])
@jwt.authenticate()
def reload_nginx():
    util.reload_nginx()

    return json_response(200, {})
