# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from datetime import timedelta
from os.path import exists, join

# 3rd party imports
import yaml

# local imports
from appconf_node import PKG_DIR
from appconf_node.core.util import cfmt



class ConfigLoader(object):
    VERSION = 1

    def __init__(self, conf_path):
        self.conf_path = conf_path or self._discover_config()

    def _discover_config(self):
        """ Find configuration file.

        The config resolution is as follows:
        - ./appconf-node.yaml
        - /etc/appconf-node.yaml
        - <appconf_node package>/run/config.yaml
        """
        resolution = [
            'appconf-node.yaml',
            '/etc/appconf-node.yaml',
            join(PKG_DIR, 'run/config.yaml'),
        ]

        conf_path = next((x for x in resolution if exists(x)), None)
        if conf_path is None:
            raise RuntimeError(
                "No configuration found. Please provide one of:\n" +
                "\n".join(resolution[:-1])
            )

        return conf_path

    def init_app(self, app):
        print(cfmt("^32Loading configuration from: ^35{}^0", self.conf_path))
        config = self._load()

        app.config.from_mapping(config)

    def _load(self):
        config = self._read()

        self._validate(config)
        self._deserialize(config)
        self._apply_defaults(config)

        return config

    def _read(self):
        try:
            # app_cfg = json.load(open(conf_path))
            with open(self.conf_path) as fp:
                config = yaml.load(fp.read())

        except yaml.YAMLError as ex:
            raise RuntimeError("Failed to load config {}: {}".format(
                self.conf_path,
                str(ex)
            ))

        return config

    def _validate(self, config):
        if 'version' not in config:
            raise RuntimeError("Unknown config version: {}".format(
                self.conf_path
            ))

        if config['version'] != ConfigLoader.VERSION:
            msg = "Unsupported config version: {}. Should be {}".format(
                config['version'], ConfigLoader.VERSION
            )
            raise RuntimeError(msg)

    def _deserialize(self, config):
        # Deserialize JSON data
        deserializers = {
            'JWT_EXPIRATION_DELTA': lambda x: timedelta(seconds=x)
        }

        for name, deserialize in deserializers.items():
            if name in config:
                config[name] = deserialize(config[name])

    def _apply_defaults(self, config):
        db_path = config.get('DB_PATH', 'db.sqlite')
        defaults = {
            'JWT_SECRET_KEY': config['SECRET_KEY'],
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///{}'.format(db_path),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'JWT_AUTH_URL_RULE': '/api/login',
            "NGINX_DIR": "/etc/nginx",
            "JWT_EXPIRATION_DELTA": timedelta(seconds=600),
            'CERT_DIR': '/etc/letsencrypt/live',
            'VERIFY_SSL_CERTS': True,
        }

        for name, value in defaults.items():
            # app_cfg[name] = value
            config.setdefault(name, value)
