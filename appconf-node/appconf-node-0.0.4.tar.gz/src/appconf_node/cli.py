# -*- coding: utf-8 -*-
# pylint: disable=redefined-builtin
""" Command line interface for appconf-node. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from getpass import getpass
from os.path import abspath, join

# os.environ.setdefault('LC_ALL', 'en_US-utf8')

# 3rd party imports
import click
import click_completion

# local imports
from appconf_node.core.util import cfmt


click_completion.init()


@click.group()
@click.option('-c', '--config', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    """ Main command group. """
    ctx.obj = {'conf_path': config and abspath(config)}


@cli.command()
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=int, default=14001)
@click.option('--no-reload', is_flag=True)
@click.pass_context
def dev(ctx, host, port, no_reload):
    opts = {'host': host, 'port': port}

    if no_reload:
        opts['use_reloader'] = False

    from appconf_node.app import init_app

    app = init_app(ctx.obj['conf_path'])
    app.run(**opts)


@cli.command()
@click.option('-h', '--host', type=str, default='127.0.0.1')
@click.option('-p', '--port', type=int, default=14001)
@click.option('-n', '--num-workers', type=int, default=2)
@click.pass_context
def start(ctx, host, port, num_workers):
    from .app import GunicornApp

    opts = {
        'bind': '{}:{}'.format(host, port),
        'workers': num_workers
    }

    from appconf_node.app import init_app

    app = init_app(ctx.obj['conf_path'])
    GunicornApp(app, opts).run()


@cli.command('create-user')
@click.argument('name', required=False)
@click.argument('email', required=False)
@click.pass_context
def create_user(ctx, name=None, email=None):
    from appconf_node.users.models import User

    name = name or input("username: ")
    email = email or input("email: ")

    while True:
        password1 = getpass("Password: ")
        password2 = getpass("Repeat: ")

        if password1 != password2:
            print("Error: Password didn't not match!")
            print("Try again.")
        else:
            break

    from appconf_node.app import init_app

    init_app(ctx.obj['conf_path'])

    user = User.create(name, password1, email)
    print("User {} created!".format(user.name))
