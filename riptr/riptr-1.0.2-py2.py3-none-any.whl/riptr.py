#!/usr/bin/env python
"""
RIP tr/sed. Python regex replacement utility.
"""
from __future__ import print_function
import argparse
import re

__version__ = '1.0.2'


def main():
    """Run some regex substitutions on cmd line files"""
    parser = argparse.ArgumentParser(
        description='Rip tr v{VERSION}'.format(VERSION=__version__))
    parser.add_argument('file', metavar='FILE', type=str, nargs='+',
                        help=('Input file(s). Combine with -w to speed this up, eg "riptr '
                              '-m <match> -s <sub> -w $(ls <dir>)"'))
    parser.add_argument('-m', '--match', metavar='REGEX', type=str,
                        help='Matching regex, python syntax', required=True)
    parser.add_argument('-s', '--substitute', metavar='REGEX', type=str,
                        help='Substitute regex, python syntax; backref groups per the --match arg.',
                        required=True)
    parser.add_argument('-i', '--inplace', action="store_true",
                        help="Edit files in place, instead of emitting to stdout")
    parser.add_argument('-d', '--dotall', action="store_true",
                        help="Set dotall on the regex")
    parser.add_argument('-l', '--multiline', action="store_true",
                        help="Set multiline on the regex")
    parser.add_argument('-v', '--version', action="store_true",
                        help="Print version and exit")
    args = parser.parse_args()

    flags = 0
    if args.dotall:
        flags += re.DOTALL
    if args.multiline:
        flags += re.MULTILINE

    matcher = re.compile(args.match, flags=flags)

    for fname in args.file:
        with open(fname, 'r') as infile:
            data = infile.read()
        data = matcher.sub(args.substitute, data)
        if args.write:
            with open(fname, 'w') as outfile:
                outfile.write(data)
        else:
            print(data)


if __name__ == '__main__':
    main()
