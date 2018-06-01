# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os

# 3rd party imports
import nginx as pynginx

# local imports
from appconf_node.core import util


def generate(
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
                proxy_pass         {name};
            }}
        }}
    """.format(
        port=port,
        name=name,
        domain=domain,
        max_body_size=max_body_size,
        host_addr=host_addr,
    )).strip() + os.linesep     # Removes the start/end empty lines.


def parse(path):
    """ Extract useful information from an nginx config file. """
    cfg = pynginx.load(open(path))

    upstreams = [
        parse_upstream(x)
        for x in cfg.children if isinstance(x, pynginx.Upstream)
    ]
    servers = [
        parse_server(x)
        for x in cfg.children if isinstance(x, pynginx.Server)
    ]

    app_server = upstreams[0]['server']
    host, port = app_server.split(':', 1)
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
