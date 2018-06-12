"""Trick Read the Docs into using Flinx."""

__version__ = '0.1.1'

import sys
from pathlib import Path
from sphinx.cmd.build import main as sphinx_build


def build(args):
    sourcedir = Path('.')  # TODO: parse SOURCEDIR from args
    if sourcedir.exists():
        print('calling sphinx with args', args)
        return sphinx_build(args)
    else:
        print('simulated call to flit')


def main():
    args = sys.argv[1:]
    print('args =', args)
    code = build(args)
    print('status =', code)
    sys.exit(code or 0)


if __name__ == '__main__':
    main()
