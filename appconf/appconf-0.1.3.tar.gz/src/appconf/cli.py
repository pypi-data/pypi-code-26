# -*- coding: utf-8 -*-
# pylint: disable=redefined-builtin
""" Command line interface for appconf. """
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import click
import click_completion

# local imports
from . import log
from . import nginx
from . import util
from . import logic


click_completion.init()


@click.group()
@click.option(
    '-c', '--conf-dir',
    type=click.Path(exists=True, file_okay=False),
    default='/etc/nginx'
)
@click.pass_context
def cli(ctx, conf_dir):
    """ Main command group. """
    ctx.obj = {'conf_dir': conf_dir}


@cli.command()
@click.argument('name')
@click.option(
    '-h', '--host-addr',
    type=str,
    default='127.0.0.1',
    help=('IP address for the host that actually has the service running. '
          'If appconf is used just to manage local services, then this will '
          'always be 127.0.0.1')
)
@click.option(
    '-p', '--port',
    type=int,
    required=True,
    help=('The port the service is running on. This combined with --host-addr '
          'forms the full proxy address this server entry will use.')
)
@click.option(
    '-d', '--domain',
    type=str,
    default=None,
    help=('The domain this service is running on. Combined with the service'
          'name this forms a full server hostname.')
)
@click.option(
    '-b', '--max-body-size',
    type=str,
    default='200M',
    help=('Maximum request body size allowed.')
)
@click.option(
    '--dry-run',
    is_flag=True,
    help=('If this flag is set, no changes will be made to the nginx '
          'configuration. It will just generate and print the app config. ')
)
@click.pass_context
def create(ctx, name, host_addr, port, domain, max_body_size, dry_run):
    """ Create new app configuration. """
    log.info("Generating app configuration for ^35{}".format(name))

    default_domain = 'novocode.net'

    if dry_run:
        app_config = nginx.gen_app_config(
            name=name,
            port=port,
            host_addr=host_addr,
            domain=domain or default_domain,
            max_body_size=max_body_size,
        )
    else:
        apps = logic.AppManager(ctx.obj['conf_dir'])
        app_config = apps.add(
            name=name,
            port=port,
            host_addr=host_addr,
            domain=domain or default_domain,
            max_body_size=max_body_size,
        )

    print(app_config)


@cli.command()
@click.option(
    '-f', '--filter',
    type=nginx.SiteFilter,
    multiple=True
)
@click.option(
    '--format',
    type=str,
    default='pretty',
    help="Output format (pretty/json)"
)
@click.pass_context
def list(ctx, filter, format):
    """ List all apps on the system. """
    apps = logic.AppManager(ctx.obj['conf_dir'])
    sites = apps.list(filter)

    if format == 'pretty':
        util.print_sites_pretty(sites)
    elif format == 'json':
        util.print_sites_json(sites)
    else:
        log.err("Invalid format {}. Supported formats are pretty/json")


@cli.command()
@click.argument('name')
@click.pass_context
def start(ctx, name):
    """ Start an app. This will require manual nginx restart afterwards. """
    log.info("Starting ^1{}".format(name))

    try:
        apps = logic.AppManager(ctx.obj['conf_dir'])
        apps.start(name)
    except logic.AppDoesNotExist:
        log.err("Site {} does not exist!".format(name))


@cli.command()
@click.argument('name')
@click.pass_context
def stop(ctx, name):
    """ Stop an app. This will require manual nginx restart afterwards. """
    log.info("Stopping ^1{}".format(name))

    try:
        apps = logic.AppManager(ctx.obj['conf_dir'])
        apps.stop(name)
    except logic.AppDoesNotExist:
        log.err("Site {} does not exist!".format(name))
