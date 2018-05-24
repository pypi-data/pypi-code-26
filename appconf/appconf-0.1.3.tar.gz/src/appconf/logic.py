# -*- coding: utf-8 -*-
""" appconf high level logic. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import abspath, exists, join, relpath

# local imports
from . import nginx
from . import util


class AppDoesNotExist(RuntimeError):
    """ Raised when app with the given name does not exist. """
    pass


class AppManager(object):
    """ Encapsulates one nginx configuration location. """
    def __init__(self, conf_dir):
        self.conf_dir = conf_dir

    def list(self, filters):
        """ Get list of existing apps. """
        sites = nginx.collect_sites(self.conf_dir)
        sites = util.filter_sites(sites, filters)
        return sites

    def add(self, name, host_addr, port, domain, max_body_size):
        """ Add new app. """
        app_config = nginx.gen_app_config(
            port=port,
            name=name,
            domain=domain,
            max_body_size=max_body_size,
            host_addr=host_addr
        )

        config_path = join(self.conf_dir, 'sites-available', name + '.conf')

        with open(config_path, 'w') as fp:
            fp.write(app_config)

        return app_config

    def start(self, name):
        """ Start an app with the given name. """
        filename = name + '.conf'

        conf_path = abspath(join(self.conf_dir, 'sites-available', filename))
        live_path = abspath(join(self.conf_dir, 'sites-enabled', filename))
        live_dir = abspath(join(self.conf_dir, 'sites-enabled'))

        if not exists(conf_path):
            raise AppDoesNotExist("Site {} does not exist!".format(name))

        if exists(live_path):
            # Already live
            return

        cwd = os.getcwd()
        try:
            os.chdir(live_dir)
            os.symlink(relpath(conf_path, live_dir), filename)
        finally:
            os.chdir(cwd)

    def stop(self, name):
        """ Stop an app with the given name. """
        filename = name + '.conf'

        conf_path = abspath(join(self.conf_dir, 'sites-available', filename))
        live_path = abspath(join(self.conf_dir, 'sites-enabled', filename))

        if not exists(conf_path):
            raise AppDoesNotExist("Site {} does not exist!".format(name))

        if not exists(live_path):
            return

        os.remove(live_path)
