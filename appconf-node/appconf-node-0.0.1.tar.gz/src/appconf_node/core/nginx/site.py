# -*- coding: utf-8 -*-
""" Single nginx site related code. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import re
from fnmatch import fnmatch
from logging import getLogger
from os.path import exists, join, splitext

# 3rd party imports
import attr
from six import string_types

# local imports
from . import conf


L = getLogger(__name__)


@attr.s
class Site(object):
    """ Represents one existing nginx site. """
    name = attr.ib()
    path = attr.ib()
    status = attr.ib('disabled')
    listen = attr.ib(default=None)
    host = attr.ib(default=None)
    port = attr.ib(default=None)
    hostname = attr.ib(default=None)
    config = attr.ib(default=None)

    @classmethod
    def fields(cls):
        """ Return the list of field names on the site instance. """
        return [field.name for field in cls.__attrs_attrs__]

    def as_row(self, fields=None):
        """ Return the selected fields as a tuple. """
        fields = fields or self.fields()
        return tuple(getattr(self, name) for name in fields)

    def as_dict(self):
        """ Return the site as a python dictionary. """
        ret = attr.asdict(self)
        del ret['config']
        return ret

    @property
    def pretty_port(self):
        if self.port is None:
            return ''
        elif (isinstance(self.port, string_types) and
              self.port.startswith('unix:/')):
            return 'unix'
        else:
            return self.port

    @classmethod
    def collect(cls, conf_dir='/etc/nginx'):
        """ Collect all sites registered with nginx. """
        sites = []
        available_path = join(conf_dir, 'sites-available')

        if exists(available_path):
            for filename in os.listdir(available_path):
                name, _ = splitext(filename)
                path = join(available_path, filename)

                live_conf_path = join(conf_dir, 'sites-enabled', filename)
                if exists(live_conf_path):
                    status = 'enabled'
                else:
                    status = 'disabled'

                try:
                    config = open(path).read()
                    parsed = conf.parse(path)
                    listen = parsed['listen']
                    host = parsed['host']
                    port = parsed['port']
                    hostname = parsed['hostname']

                except IOError:
                    status = 'broken'
                    config = 'File not found'
                    listen = host = port = hostname = None

                sites.append(Site(
                    name=name,
                    path=path,
                    status=status,
                    listen=listen,
                    host=host,
                    port=port,
                    hostname=hostname,
                    config=config,
                ))

        return sites


class SiteFilter(object):
    """ Filter for site lists. """
    RE_FILTER = re.compile(r'[\w\d_]+=.*')

    def __init__(self, field, pattern):
        self.field = field
        self.pattern = pattern

    @classmethod
    def from_string(cls, value):
        if not SiteFilter.RE_FILTER.match(value):
            raise ValueError(
                'Invalid filter. '
                'The filter should be in format <attr>=<value query>'
            )
        field, pattern = value.split('=')

        if field not in Site.fields():
            raise ValueError(
                'Invalid filter field. Must be one of: '
                '/'.join(Site.fields())
            )

        return SiteFilter(field, pattern)

    def __repr__(self):
        """ Return the filter in pretty format"""
        return '{} = {}'.format(self.field, self.pattern)

    def match(self, site):
        """ Return True if the site matches the filter. """
        if hasattr(site, self.field):
            value = getattr(site, self.field)

            if fnmatch(str(value), self.pattern):
                return True

        return False
