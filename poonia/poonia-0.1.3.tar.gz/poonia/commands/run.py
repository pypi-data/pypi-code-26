import click
import os, sys, fnmatch, glob
from . import pglob

fs_encoding = sys.getfilesystemencoding()

@click.command(help='Run a command for files matching a pattern')
@click.argument('pattern', nargs=1)
@click.argument('command', nargs=-1, required=True)
@click.option('--verbose/--quiet', default=True)
@click.option('-r', '--recurse', is_flag=True)
def run(pattern, command, verbose, recurse):
    e = lambda x: '"%s"' % x if ' ' in x else x

    for fn in pglob(pattern, recurse=recurse):
        cmd = ' '.join(e(x) if x != '{}' else e(fn) for x in command)
        if verbose:
            click.secho(cmd, bg='green', fg='white', bold=True, err=True)
        os.system(cmd.encode(fs_encoding))

@click.command(help='Run a command / expand a pattern')
@click.argument('pattern', nargs=1)
@click.argument('command', nargs=-1, required=True)
@click.option('--verbose/--quiet', default=True)
@click.option('-r', '--recurse', is_flag=True)
def rune(pattern, command, verbose, recurse):
    e = lambda x: '"%s"' % x if ' ' in x else x
    fns = ' '.join(e(x) for x in pglob(pattern, recurse=recurse))
    cmd = ' '.join(e(x) if x != '{}' else fns for x in command)
    if verbose:
        click.secho(cmd, bg='green', fg='white', bold=True, err=True)
    os.system(cmd.encode(fs_encoding))
