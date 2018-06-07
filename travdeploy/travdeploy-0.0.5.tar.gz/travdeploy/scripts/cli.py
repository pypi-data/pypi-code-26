# Skeleton of a CLI

import click

import travdeploy


@click.command('travdeploy')
@click.argument('count', type=int, metavar='N')
def cli(count):
    """Echo a value `N` number of times"""
    for i in range(count):
        click.echo(travdeploy.has_legs)
