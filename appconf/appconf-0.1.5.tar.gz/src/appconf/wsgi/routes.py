# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
from os.path import abspath, dirname, join

# 3rd party imports
from flask import request, redirect
from jinja2 import Environment, PackageLoader, select_autoescape

# local imports
from . import app
from .. import logic
from .. import nginx


TEMPLATE_DIR = join(abspath(dirname(__file__)), 'templates')
env = Environment(
    loader=PackageLoader('appconf.wsgi', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def json_response(code, data, headers=None):
    headers = dict(headers or {})
    headers['Content-Type'] = 'application/json'

    return json.dumps(data), code, headers


@app.route('/login', methods=['get'])
def login_form():
    """ List all apps on the system. """
    template = env.get_template('login.html')
    return template.render()


@app.route('/login', methods=['post'])
def login():
    """ List all apps on the system. """
    args = request.form if request.json is None else request.json
    username = args.get('username')
    password = args.get('password')

    return json_response(200, {
        'username': username,
        'password': password
    })


@app.route('/')
def index():
    apps = logic.AppManager(app.config['CONF_DIR'])
    sites = apps.list([])

    template = env.get_template('index.html')

    fields = nginx.Site.fields()
    fields.remove('config')
    fields.remove('path')

    return template.render(
        fields=fields,
        sites=sites,
        next='/'
    )


@app.route('/apps')
def list():
    """ List all apps on the system. """
    apps = logic.AppManager(app.config['CONF_DIR'])
    sites = apps.list([])

    return json_response(200, [
        site.as_dict() for site in sites
    ])


@app.route('/add', methods=['get'])
def add_form():
    default_domain = 'novocode.net'
    default_host = '127.0.0.1'

    return env.get_template('add.html').render(**locals())


@app.route('/add', methods=['post'])
def add():
    args = request.form if request.json is None else request.json
    next = request.form.get('next')

    if not args['name']:
        return json_response(400, {'detail': 'name is required'})

    if not args['port']:
        return json_response(400, {'detail': 'port is required'})

    app_config = {
        'name': args['name'],
        'port': args['port'],
        'host_addr': args.get('host_addr', '127.0.0.1'),
        'max_body_size': args.get('max_body_size', '20M'),
        'domain': args.get('domain', 'novocode.net'),
    }

    apps = logic.AppManager(app.config['CONF_DIR'])
    apps.add(**app_config)

    if next is not None:
        return redirect(next)
    else:
        return json_response(201, app_config)


@app.route('/delete/<name>', methods=['post'])
def delete(name):
    next = request.form.get('next')
    apps = logic.AppManager(app.config['CONF_DIR'])

    try:
        apps.delete(name)

        if next is not None:
            return redirect(next)
        else:
            return json_response(201, app_config)
    except logic.AppDoesNotExist:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })


@app.route('/start/<name>', methods=['post'])
def start(name):
    next = request.form.get('next')

    try:
        apps = logic.AppManager(app.config['CONF_DIR'])
        apps.start(name)

        if next is not None:
            return redirect(next)
        else:
            return json_response(200, {
                'detail': "'{}' has  been started".format(name)
            })
    except logic.AppDoesNotExist:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })


@app.route('/stop/<name>', methods=['post'])
def stop(name):
    next = request.form.get('next')

    try:
        apps = logic.AppManager(app.config['CONF_DIR'])
        apps.stop(name)

        if next is not None:
            return redirect(next)
        else:
            return json_response(200, {
                'detail': "'{}' has  been started".format(name)
            })
    except logic.AppDoesNotExist:
        return json_response(400, {
            'detail': "'{}' does not exist!".format(name)
        })
