# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import join

# 3rd party imports
from flask import send_from_directory, send_file

# local imports
from appconf import logic
from appconf import nginx
from .. import app
from .common import jinja, WEBAPP_DIR


DIST_DIR = join(WEBAPP_DIR, 'static')


@app.route('/dist/<path:path>')
def frontend_files(path):
    return send_from_directory(DIST_DIR, path)


@app.route('/dash')
def dashboard():
    apps = logic.AppManager(app.config['CONF_DIR'])
    sites = apps.list([])

    template = jinja.get_template('index.html')

    fields = nginx.Site.fields()
    fields.remove('config')
    fields.remove('path')

    return template.render(
        fields=fields,
        sites=sites,
        next='/'
    )


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    print("CATCH-ALL: {}".format(path))
    return send_file(join(DIST_DIR, 'index.html'))
