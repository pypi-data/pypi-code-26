import click
import json
import yaml
import random
import string

from binx.binx import Binx

# Not sure why this is not default...
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('action', 
                type=click.Choice(['random']))
@click.option('--length',
              required=True,
              help='Provide a lenght of the random string')
@click.option('--prefix',
              default="",
              help='Provide a prefix')
def main(**kwargs):

    # initilize binx
    binx = Binx(**kwargs)

    # fire a command
    response = binx.random()

    # print the command
    print(response)

if __name__ == '__main__':
    main()