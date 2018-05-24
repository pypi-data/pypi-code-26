# -*- coding: utf-8 -*-
""" nginx related code. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import re
from fnmatch import fnmatch
from os.path import exists, join, splitext

# 3rd party imports
import attr
import nginx as pynginx

# local imports
from . import nginx
from . import util


# Site = namedtuple('Site', 'name path status listen host port hostname config')


@attr.s
class Site(object):
    """ Represents one existing nginx site. """
    name = attr.ib()
    path = attr.ib()
    status = attr.ib('stopped')
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
        return attr.asdict(self)


class SiteFilter(object):
    """ Filter for site lists. """
    RE_FILTER = re.compile(r'[\w\d_]+=.*')

    def __init__(self, value):
        if not SiteFilter.RE_FILTER.match(value):
            raise ValueError(
                'Invalid filter. '
                'The filter should be in format <attr>=<value query>'
            )
        self.field, self.pttrn = value.split('=')

        if self.field not in nginx.Site.fields():
            raise ValueError(
                'Invalid filter field. Must be one of: '
                '/'.join(nginx.Site.fields())
            )

    def __repr__(self):
        """ Return the filter in pretty format"""
        return '{} = {}'.format(self.field, self.pttrn)

    def match(self, site):
        """ Return True if the site matches the filter. """
        if hasattr(site, self.field):
            value = getattr(site, self.field)

            if fnmatch(str(value), self.pttrn):
                return True

        return False


def parse_config(path):
    """ Extract usefull information from an nginx config file. """
    cfg = pynginx.load(open(path))

    upstreams = [
        parse_upstream(x)
        for x in cfg.children if isinstance(x, pynginx.Upstream)
    ]
    servers = [
        parse_server(x)
        for x in cfg.children if isinstance(x, pynginx.Server)
    ]

    host = upstreams[0]['host']
    port = upstreams[0]['port']
    domain = servers[0]['domain']
    hostname = servers[0]['hostname']
    listen = '/'.join(s['listen'] for s in servers)

    assert len(set(s['hostname'] for s in servers)) == 1

    return {
        'listen': listen,
        'host': host,
        'port': port,
        'domain': domain,
        'hostname': hostname
    }


def parse_upstream(upstream):
    """ Parse upstream entry in nginx config. """
    name = upstream.as_list[1]
    server = upstream.as_list[2][0][1]

    if server.startswith('unix:/'):
        host = 'localhost'
        port = server.split(maxsplit=1)[0]
    else:
        parts = server.rsplit(':', maxsplit=1)
        host, port = parts
        if port.isdigit():
            port = int(port)

    return {
        'name': name,
        'server': server,
        'host': host,
        'port': port
    }


def parse_server(server):
    """ Parse server entry in nginx config. """
    listen = _get_key(server, 'listen')
    hostname = _get_key(server, 'server_name')
    name, domain = hostname.split('.', maxsplit=1)

    return {
        'hostname': hostname,
        'name': name,
        'domain': domain,
        'listen': listen,
    }


def _get_key(server, name):
    """ Return the value for the key with the given name. """
    return next((k.value for k in server.children if k.name == name), None)


def collect_sites(conf_dir='/etc/nginx'):
    """ Collect all sites registered with nginx. """
    sites = []
    available_path = join(conf_dir, 'sites-available')

    if exists(available_path):
        for filename in os.listdir(available_path):
            name, _ = splitext(filename)
            path = join(available_path, filename)

            live_conf_path = join(conf_dir, 'sites-enabled', filename)
            if exists(live_conf_path):
                status = 'live'
            else:
                status = 'stopped'

            try:
                config = open(path).read()
                parsed = parse_config(path)
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


def gen_app_config(
        port, name, domain,
        max_body_size='200M',
        host_addr='127.0.0.1'
):
    """ Generate new nginx configuration for an app. """
    return util.remove_indent("""
        upstream {name} {{
            server {host_addr}:{port};
            keepalive 60;
        }}


        server {{
            listen                  80;
            server_name             {name}.{domain};
            client_max_body_size    {max_body_size};

            access_log /var/log/nginx/{name}/access.log;
            error_log /var/log/nginx/{name}/error.log;

            location / {{
                proxy_pass         http://{name};
                proxy_set_header   Host             $host;
                proxy_set_header   X-Real-IP        $remote_addr;
                proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
                proxy_set_header   X-Forwarded-Host $server_name;
            }}
        }}
    """.format(
        port=port,
        name=name,
        domain=domain,
        max_body_size=max_body_size,
        host_addr=host_addr,
    )).strip() + os.linesep     # Removes the start/end empty lines.
