import subprocess

from ngrp.config_writer import ConfigWriter
from ngrp.metainfo import with_headers
from ngrp.templates import HttpReverseProxyTemplate


def add_domain_config(template, force, **kwargs):
    domain = kwargs.get("domain")
    config_writer = ConfigWriter(domain)
    config_str = template.format(**kwargs)
    config_str = with_headers(config_str, template_class=type(template))
    config_writer.write(config_str, force=force)


def enable_domain_config(domain, force):
    config_writer = ConfigWriter(domain)
    config_writer.enable_config(force=force)


def disable_domain_config(domain):
    config_writer = ConfigWriter(domain)
    config_writer.disable_config()


def reload_nginx_config():
    try:
        nginx_out = subprocess.run("/usr/sbin/nginx -s reload".split(), stderr=subprocess.PIPE)
        nginx_out.check_returncode()
    except FileNotFoundError:
        raise NginxNotFoundError
    except subprocess.CalledProcessError:
        raise NginxPermissionError


class NginxNotFoundError(BaseException):
    pass


class NginxPermissionError(BaseException):
    pass
