import sys
import click
import psycopg2
from .users import Users

@click.group()
@click.option('--debug', is_flag=True)
@click.option('--dsn', default='postgresql://dpuser:dpuser@localhost:5432/accounts', type=str, envvar='DB_DSN')
@click.pass_context
def cli(ctx, debug, dsn):
    try:
        users = Users(dsn)
    except psycopg2.OperationalError as e:
        print("ERROR: Could not connect to the database")
        if debug:
            raise
        sys.exit(1)
    # create the tables if they don't exist
    users.create()
    ctx.users = users


@cli.command()
@click.argument('user', type=str)
@click.argument('password', type=str)
@click.pass_context
def add(ctx, user, password):
    users = ctx.parent.users
    try:
        users.add(user, password)
    except KeyError:
        print("ERROR: User already exists")
        sys.exit(1)


@cli.command()
@click.argument('user', type=str)
@click.argument('password', type=str)
@click.pass_context
def set(ctx, user, password):
    users = ctx.parent.users
    try:
        users.set(user, password)
    except KeyError:
        print("User doesn't exist")
        sys.exit(1)


@cli.command()
@click.argument('user', type=str)
@click.argument('password', type=str)
@click.pass_context
def remove(ctx, user):
    users = ctx.parent.users
    try:
        users.remove(user)
    except KeyError:
        print("User doesn't exist")
        sys.exit(1)


if __name__ == '__main__':
    cli()
