import click
import os, sys, glob

@click.command(help='Search PATH')
@click.argument('pattern')
def which(pattern):
    path_dirs = os.environ.get('PATH', '').split(';')
    for d in path_dirs:
        for f in glob.glob(os.path.join(d, pattern)):
            click.echo(f)
