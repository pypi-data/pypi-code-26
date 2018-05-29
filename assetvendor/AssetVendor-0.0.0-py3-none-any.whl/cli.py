from argparse import ArgumentParser

from .commands.check import Check
from .commands.init import Init
from .commands.install import Install


def main(args=None):
    parser = ArgumentParser()

    # https://github.com/python/cpython/pull/3027
    subparsers = parser.add_subparsers()
    subparsers.required = True

    # Initialize subcommands, add arguments to parser and set handler
    subcommands = [(cls.__name__.lower(), cls()) for cls in [Init, Install, Check]]
    for name, command in subcommands:
        subparser = subparsers.add_parser(name, description=command.__doc__)
        subparser.set_defaults(func=command.handle)
        command.add_arguments(subparser)

    # Redirect to subcommand handler
    options = parser.parse_args(args)
    if hasattr(options, 'func'):
        return options.func(options)
    return parser.print_help()
