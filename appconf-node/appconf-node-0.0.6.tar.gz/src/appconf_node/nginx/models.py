# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from enum import Enum
from os.path import abspath, exists, join, relpath, lexists

# local imports
from appconf_node.app import app, db
from . import util


SECRET_KEY = app.config['SECRET_KEY']


class SiteProto(Enum):
    Http = 'http'
    Https = 'https'


class SiteStatus(Enum):
    Enabled = 'enabled'
    Disabled = 'disabled'
    Broken = 'broken'


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    domain = db.Column(db.String(200))
    app_proto = db.Column(db.String(10), default='http')
    app_addr = db.Column(db.String(500))

    @property
    def hostname(self):
        return '{0.name}.{0.domain}'.format(self)

    @property
    def status(self):
        if not hasattr(self, '_status'):
            self._status = util.site_status(self)

        return self._status

    @property
    def config(self):
        if not hasattr(self, '_config'):
            self._config = util.generate_config(self)

        return self._config

    @property
    def config_file(self):
        if not hasattr(self, '_config_file'):
            sites_dir = abspath(join(app.config['NGINX_DIR'], 'sites-enabled'))
            self._config_file = join(sites_dir, 'appconf-{}.conf'.format(
                self.hostname
            ))

        return self._config_file

    @property
    def ssl_cert(self):
        if not hasattr(self, '_ssl_cert'):
            cert_dir = abspath(app.config['CERT_DIR'])
            self._ssl_cert = join(cert_dir, self.hostname, 'fullchain.pem')

        return self._ssl_cert

    @property
    def ssl_key(self):
        if not hasattr(self, '_ssl_key'):
            cert_dir = abspath(app.config['CERT_DIR'])
            self._ssl_key = join(cert_dir, self.hostname, 'fullchain.pem')

        return self._ssl_key

    def start(self):
        if self.status != 'disabled':
            raise ValueError(
                "Cannot enable app [status: '{}']".format(self.status)
            )

        with open(self.config_file, 'w') as fp:
            fp.write(self.config)

        # Invalidate status cache
        del self._status

    def stop(self):
        if self.status != 'enabled':
            raise ValueError(
                "Cannot disable app [status: '{}']".format(self.status)
            )

        if exists(self.config_file):
            os.remove(self.config_file)

        # Invalidate status cache
        del self._status

