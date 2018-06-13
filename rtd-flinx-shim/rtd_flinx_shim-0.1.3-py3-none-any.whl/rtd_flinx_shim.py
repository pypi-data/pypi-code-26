"""Trick Read the Docs into using Flinx."""

import subprocess
import sys
from pathlib import Path

from sphinx.cmd.build import main as sphinx_build

__version__ = "0.1.3"


def cli():
    args = sys.argv[1:]
    print('flynx invocation:')
    print('args =', args)
    process = subprocess.run(['flinx', 'generate'] + args)
    sys.stderr.write("Flynx exited with status={}\n".format(process.returncode))
    code = sphinx_build(args)
    sys.exit(code or 0)


if __name__ == 'cli':
    sys.exit(cli())
