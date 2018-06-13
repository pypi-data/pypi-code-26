"""Trick Read the Docs into using Flinx."""

import sys
from pathlib import Path
from sphinx.cmd.build import main as sphinx_build


def main(args):
    sourcedir = Path('.')  # TODO: parse SOURCEDIR from args
    if sourcedir.exists():
        print('calling sphinx with args', args)
        return sphinx_build(args)
    else:
        print('simulated flynx invocation:')
        print('flynx generate --no-overwrite --write-requirements')


def cli():
    args = sys.argv[1:]
    print('args =', args)
    code = main(args)
    print('status =', code)
    sys.exit(code or 0)


if __name__ == 'cli':
    sys.exit(cli())
