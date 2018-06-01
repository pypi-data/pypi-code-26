# -*- coding: utf-8 -*-
# pylint: disable=redefined-builtin
""" Command line interface for appconf-node. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from getpass import getpass

# os.environ.setdefault('LC_ALL', 'en_US-utf8')

# 3rd party imports
import click
import click_completion

# local imports


click_completion.init()


def load_flask_app():
    from appconf_node.app import app, init_app

    app.app_context().push()
    init_app()

    return app


@click.group()
@click.option('-c', '--config', type=click.Path(exists=True))
@click.pass_context
def cli(ctx, config):
    """ Main command group. """
    ctx.obj = {'conf_path': config}


@cli.command()
@click.option('-h', '--host', type=str, default='0.0.0.0')
@click.option('-p', '--port', type=int, default=14001)
@click.option('--no-reload', is_flag=True)
@click.pass_context
def webui(ctx, host, port, no_reload):
    opts = {'host': host, 'port': port}

    if no_reload:
        opts['use_reloader'] = False

    app = load_flask_app()
    app.run(**opts)


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

    load_flask_app()

    user = User.create(name, password1, email)
    print("User {} created!".format(user.name))
