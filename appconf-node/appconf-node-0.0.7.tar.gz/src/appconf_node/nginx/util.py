# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import signal
from os.path import abspath, exists, join, lexists
from subprocess import call

# 3rd party imports
from flask import current_app as app
import psutil

# local imports
from appconf_node.core import util


def reload_nginx():
    nginx = next((x for x in psutil.process_iter() if x.name() == 'nginx'),
                 None)

    if nginx:
        os.kill(nginx.pid, signal.SIGHUP)
        return True

    return False


def generate_config(site):
    return util.remove_indent("""
upstream {name} {{
    server {app_addr};
    keepalive 60;
}}

server {{
    listen          80;
    server_name     {name}.{domain};

    return 301 https://{name}.{domain}/$request_uri;
}}

server {{
    listen                  443 ssl;
    server_name             {name}.{domain};

    access_log /var/log/nginx/sites/{name}-access.log;
    error_log /var/log/nginx/sites/{name}-error.log;
    
    ssl_certificate         /etc/letsencrypt/live/{name}.{domain}/fullchain.pem;
    ssl_certificate_key     /etc/letsencrypt/live/{name}.{domain}/privkey.pem;

    location / {{
        proxy_pass         {app_proto}://{name};
       
        proxy_set_header   Host             $host;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Host $server_name;
    }}
}}
        """.format(
        name=site.name,
        domain=site.domain,
        app_proto=site.app_proto,
        app_addr=site.app_addr,
    )).strip() + os.linesep     # Removes the start/end empty lines.


def site_status(site):
    if app.config['VERIFY_SSL_CERTS']:
        if not (lexists(site.ssl_cert) and lexists(site.ssl_key)):
            return 'broken'

    if exists(site.config_file):
        return 'enabled'
    else:
        return 'disabled'
