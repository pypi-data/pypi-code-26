from contextlib import contextmanager
from functools import wraps
import sys

import click

from ngrp import ngrp
from ngrp.config_writer import (ConfigFileExistsError,
                                ConfigLinkConflictError,
                                ConfigLinkExistsError)
from ngrp.templates import (HttpReverseProxyTemplate,
                            HttpsReverseProxyTemplate,
                            StaticPageHttpTemplate,
                            StaticPageHttpsTemplate)

FORCE_MESSAGE = "Override existing files."


def template_command(template_class):
    """
    Dynamically creates a command for a template class.
    Adds parameteres according to template string.
    """
    def wrapper(f):
        template = template_class()

        @wraps(f)
        def wrapped(**kwargs):
            return f(template=template, **kwargs)
        for param in reversed(template.parameters):
            click.argument(param)(wrapped)
        return wrapped
    return wrapper


@click.group()
@click.version_option()
def ngrp_command():
    """Nginx domains configuration tool."""


@ngrp_command.group()
def add():
    """Add and enable a domain configuration."""


templates = {
    "http": (HttpReverseProxyTemplate, "Redirect DOMAIN traffic to 127.0.0.1:PORT"),
    "https": (HttpsReverseProxyTemplate, "Redirect DOMAIN traffic to 127.0.0.1:PORT"),
    "static-http": (StaticPageHttpTemplate, "Serve content from WEBSITE_ROOT on DOMAIN"),
    "static-https": (StaticPageHttpsTemplate, "Serve content from WEBSITE_ROOT on DOMAIN"),
}

for command, (template_class, help_) in templates.items():
    @add.command(name=command, help=help_)
    @template_command(template_class)
    @click.option("--force", "-f", default=False, is_flag=True, help=FORCE_MESSAGE)
    def add_template(**kwargs):
        with error_handler():
            ngrp.add_domain_config(**kwargs)


@ngrp_command.command()
@click.argument("domain")
@click.option("--force", "-f", default=False, is_flag=True, help=FORCE_MESSAGE)
def enable(domain, force):
    """Enable configuration for given domain."""
    with error_handler():
        ngrp.enable_domain_config(domain, force)


@ngrp_command.command()
@click.argument("domain")
def disable(domain):
    """Disable configuration for given domain."""
    with error_handler():
        ngrp.disable_domain_config(domain)


@ngrp_command.command()
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
