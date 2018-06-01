# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from flask import request, redirect

# local imports
from appconf_node.core.nginx import site_manager
from appconf_node.app import app
from appconf_node.users.auth import jwt_required
from appconf_node.core.api import json_response


@app.route('/api/app')
@jwt_required()
def app_list():
    """ List all apps on the system. """
    apps = site_manager.SiteManager(app.config['NGINX_DIR'])
    sites = apps.list([])

    return json_response(200, [
        site.as_dict() for site in sites
    ])


@app.route('/api/app', methods=['post'])
def app_create():
    args = request.form if request.json is None else request.json
    next = request.form.get('next')

    if not request.json['name']:
        return json_response(400, {'detail': 'name is required'})

    if not request.json['port']:
        return json_response(400, {'detail': 'port is required'})

    site = {
        'name': request.json['name'],
        'port': request.json['port'],
        'host_addr': request.json.get('host_addr', '127.0.0.1'),
        'max_body_size': request.json.get('max_body_size', '20M'),
        'domain': request.json.get('domain', 'novocode.net'),
    }

    sites = site_manager.SiteManager(app.config['NGINX_DIR'])
    sites.add(**site)

    return json_response(201, site)


@app.route('/api/app/<name>', methods=['delete'])
def app_delete(name):
    next = request.form.get('next')
    sites = site_manager.SiteManager(app.config['NGINX_DIR'])

    try:
        sites.delete(name)

        if next is not None:
            return redirect(next)
        else:
            return json_response(204, {})
    except site_manager.AppDoesNotExist:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })


@app.route('/api/app/<name>/config')
def app_config(name):
    """ List all apps on the system. """
    apps = site_manager.SiteManager(app.config['NGINX_DIR'])
    webapp = apps.get(name)

    if webapp is None:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })

    return webapp.config, 200, {'Content-Type': 'text/plain'}


@app.route('/api/app/<name>/start', methods=['post'])
def app_start(name):
    next = request.form.get('next')

    try:
        apps = site_manager.SiteManager(app.config['NGINX_DIR'])
        apps.start(name)

        if next is not None:
            return redirect(next)
        else:
            webapp = apps.get(name)
            return json_response(200, {
                'detail': "'{}' has  been started".format(name),
                'app': webapp.as_dict()
            })
    except site_manager.AppDoesNotExist:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })


@app.route('/api/app/<name>/stop', methods=['post'])
def app_stop(name):
    next = request.form.get('next')

    try:
        apps = site_manager.SiteManager(app.config['NGINX_DIR'])
        apps.stop(name)

        if next is not None:
            return redirect(next)
        else:
            webapp = apps.get(name)
            return json_response(200, {
                'detail': "'{}' has  been started".format(name),
                'app': webapp.as_dict()
            })
    except site_manager.AppDoesNotExist:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })
