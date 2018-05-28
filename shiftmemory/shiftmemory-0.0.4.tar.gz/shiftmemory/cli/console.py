#!/usr/bin/env python3
import click
from click import echo, style


# -----------------------------------------------------------------------------
# Group setup
# -----------------------------------------------------------------------------

class Config():
    """
    Config object
    Click context object that allows you to communicate data between groups
    and commands
    """
    def __init__(self):
        self.verbose = False

configurator = click.make_pass_decorator(Config, ensure=True)


@click.group(
    help=style(fg='yellow', text='''Welcome to shiftmemory console\n
    You can use it to perform various management operations on your configured
    caches like getting stats, optimizing and clearing caches by namespace
    or tag sets.
    '''
))
@click.option(
    '--config',
    type=click.File('r'),
    default='shiftmemory.cfg',
    required=False,
    help='Your caches configuration'
)
@configurator
def cli(settings, config):
    """ Main command group """
    settings.config = config

# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------



# @cli.command(name='list-caches')
def caches():
    """ List configured caches """

    br()
    cyan('Listing caches'.upper())
    cyan('-'*80)
    br(3)


# @cli.command(name='stats')
def stats():
    """ Display cache stats """

    br()
    cyan('Displaying cache stats'.upper())
    cyan('-'*80)
    br(3)


# @cli.command(name='delete')
# @click.option('--key', type= str, default=None, help='Item key to delete')
# @click.option('--tags', type= str, default=None, help='Tags to delete by')
def delete(key=None, tags=None):
    """ Delete cached items by key or tags  """

    if key: msg = 'Deleting item by key "{}"'.format(key)
    if tags: msg = 'Deleting item by tags [{}]'.format(tags)

    br()
    cyan(msg.upper())
    cyan('-'*80)
    br(3)


# @cli.command(name='delete-cache')
# @click.argument('name', type=str, required=True)
def delete_cache(name):
    """ Delete all items in cache by name """

    br()
    cyan('Dropping cache "{}"'.upper().format(name))
    cyan('-'*80)
    br(3)


# @cli.command(name='delete-all-caches')
def delete_all_caches():
    """ Delete all caches """
    br()
    cyan('Clearing out all caches'.upper())
    cyan('-'*80)
    br(3)


# @cli.command(name='optimize')
# @click.argument('name', type=str, required=True)
def optimize(name):
    """ Optimize cache """
    br()
    cyan('Optimizing cache "{}"'.upper().format(name))
    cyan('-'*80)
    br(3)


# @cli.command(name='optimize-all')
def optimize_all():
    """ Optimize all caches """

    br()
    cyan('Optimizing all caches'.upper())
    cyan('-'*80)
    br(3)



# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def br(how_much=1): echo('\n' * how_much)
def green(text): echo(style(text, fg='green'))
def yellow(text): echo(style(text, fg='yellow'))
def red(text): echo(style(text, fg='red'))
def blue(text): echo(style(text, fg='blue'))
def cyan(text): echo(style(text, fg='cyan'))
def magenta(text): echo(style(text, fg='magenta'))
