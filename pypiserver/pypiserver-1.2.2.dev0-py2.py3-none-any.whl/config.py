"""Define utilities for parsing and consuming config options."""

import re
from argparse import ArgumentParser
from textwrap import dedent


_AUTH_RE = re.compile(r'[, ]+')
_AUTH_ACTIONS = ('download', 'list', 'update')


def auth_parse(auth_str):
    """Parse the auth string to yield a list of authenticated actions.

    :param str auth_str: a string of comma-separated auth actions

    :return: a list of validated auth actions
    :rtype: List[str]
    """
    authed = [
        a.lower() for a in _AUTH_RE.split(auth_str.strip(' ,')) if a
    ]
    if len(authed) == 1 and authed[0] == '.':
        return []
    for a in authed:
        if a not in _AUTH_ACTIONS:
            errmsg = 'Authentication action "%s" not one of %s!'
            raise ValueError(errmsg % (a, _AUTH_ACTIONS))
    return authed


def get_parser():
    """Return an argument parser."""
    parser = ArgumentParser(
        description='start PyPI compatible package server'
    )

    server = parser.add_argument_group('server')
    server.add_argument(
        'root', default=['~/packages'], action='append', nargs='*',
        help=(dedent('''\n
            serve packages from the specified root directory. Multiple
            root directories may be specified. If no root directory is
            provided, %(default)s will be used. Root directories will
            be scanned recursively for packages. Files and directories
            starting with a dot are ignored.
        '''))
    )
    server.add_argument(
        '-i', '--interface', default='0.0.0.0', dest='host',
        help=('listen on interface INTERFACE (default: %(default)s, '
              'any interface)')
    )
    server.add_argument(
        '-p', '--port', default=8080, type=int,
        help='listen on port PORT (default: %(default)s)'
    )
    server.add_argument(
        '--fallback-url', default='https://pypi.org/simple',
        help=('for packages not found in the local index, return a '
              'redirect to this URL (default: %(default)s)')
    )
    server.add_argument(
        '--disable-fallback', action='false', default=True,
        dest='redirect_to_fallback',
        help=('disable redirect to real PyPI index for packages not found '
              'in the local index')
    )

    security = parser.add_argument_group('security')
    # TODO: pull some of this long stuff out into an epilog
    security.add_argument(
        '-a', '--authenticate', type=auth_parse, default=['update'],
        help=dedent('''\n
            comma-separated list of (case-insensitive) actions to
            authenticate. Use "." for no authentication. Requires the
            password (-P option) to be set. For example to password-protect
            package downloads (in addition to uploads), while leaving
            listings public, use: `-P foo/htpasswd.txt`  -a update,download
            To drop all authentications, use: `-P .  -a `.
            Note that when uploads are not protected, the `register`
            command is not necessary, but `~/.pypirc` still requires
            username and password fields, even if bogus. By default,
            only %(default)s is password-protected.
        ''')
    )
    security.add_argument(
        '-P', '--passwords', dest='password_file',
        help=dedent('''\n
            use apache htpasswd file PASSWORD_FILE to set usernames &
            passwords when authenticating certain actions (see -a option).
            If you want to allow un-authorized access, set this option and -a
            to '.'.
        ''')
    )
