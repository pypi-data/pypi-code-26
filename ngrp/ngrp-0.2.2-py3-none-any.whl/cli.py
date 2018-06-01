from contextlib import contextmanager
from functools import wraps
import sys

import click

from ngrp import ngrp
from ngrp.config_writer import (ConfigFileExistsError,
                                ConfigLinkConflictError,
                                ConfigLinkExistsError)
from ngrp.templates import (HttpReverseProxyTemplate,
                            HttpsReverseProxyTemplate)

FORCE_MESSAGE = "Override existing files."


def template_command(command, template_class, help_):
    """
    Dynamically creates a command for a template class.
    Adds parameteres according to template string.
    """
    def wrapper(f):
        template = template_class()
        @wraps(f)
        def wrapped(**kwargs):
            return f(template=template, **kwargs)
        wrapped.__name__ = command
        wrapped.__doc__ = help_
        for param in reversed(template.parameters):
            click.argument(param)(wrapped)
        return wrapped
    return wrapper


@click.group()
def reverse_proxy():
    """Nginx reverse proxy configuration tool."""


@reverse_proxy.group()
def add():
    """Add and enable a reverse proxy."""

templates = {
    "http": (HttpReverseProxyTemplate, "Redirect DOMAIN traffic to 127.0.0.1:PORT"),
    "https": (HttpsReverseProxyTemplate, "Redirect DOMAIN traffic to 127.0.0.1:PORT"),
} 

for command, (template_class, help_) in templates.items():
    @add.command()
    @template_command(command, template_class, help_)
    @click.option("--force", "-f", default=False, is_flag=True, help=FORCE_MESSAGE)
    def add_template(**kwargs):
        with error_handler():
            ngrp.add_reverse_proxy(**kwargs)


@reverse_proxy.command()
@click.argument("domain")
@click.option("--force", "-f", default=False, is_flag=True, help=FORCE_MESSAGE)
def enable(domain, force):
    """Enable proxy for given domain."""
    with error_handler():
        ngrp.enable_reverse_proxy(domain, force)


@reverse_proxy.command()
@click.argument("domain")
def disable(domain):
    """Disable proxy for given domain."""
    with error_handler():
        ngrp.disable_reverse_proxy(domain)


@reverse_proxy.command()
def reload():
    """Reload nginx configuration."""
    with error_handler():
        ngrp.reload_nginx_config()


@contextmanager
def error_handler():
    try:
        yield
    except ConfigLinkExistsError as e:
        sys.exit("Configuration file link already exists under {}.".format(e.filepath))
    except ConfigFileExistsError as e:
        sys.exit("Configuration file already exists under {}.".format(e.filepath))
    except ConfigLinkConflictError as e:
        sys.exit("{} is not a link.".format(e.filepath))
    except PermissionError as e:
        sys.exit("You don't have write permission to {}.".format(e.filename))
    except ngrp.NginxPermissionError:
        sys.exit("You don't have permission to control nginx runtime.")
    except ngrp.NginxNotFoundError:
        sys.exit("nginx binary not in the $PATH")
