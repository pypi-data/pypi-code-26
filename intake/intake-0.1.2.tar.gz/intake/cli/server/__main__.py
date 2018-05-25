from __future__ import print_function

import argparse
import signal
import sys

import tornado.ioloop
import tornado.web

from .server import IntakeServer
from .config import conf
from intake.catalog import Catalog


def call_exit_on_sigterm(signal, frame):
    sys.exit(0)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description='Intake Catalog Server')
    parser.add_argument('-p', '--port', type=int, default=conf['port'],
                        help='port number for server to listen on')
    parser.add_argument('--sys-exit-on-sigterm', action='store_true',
                        help='internal flag used during unit testing to ensure .coverage file is written')
    parser.add_argument('catalog_args', metavar='FILE', type=str, nargs='+',
                        help='Name of catalog YAML file')
    args = parser.parse_args(argv[1:])

    if args.sys_exit_on_sigterm:
        signal.signal(signal.SIGTERM, call_exit_on_sigterm)

    print('Creating catalog from:')
    for arg in args.catalog_args:
        print('  - %s' % arg)

    print("catalog_args", args.catalog_args)
    catalog = Catalog(args.catalog_args)

    print('Entries:', ','.join(list(catalog)))

    print('Listening on port %d' % args.port)

    server = IntakeServer(catalog)
    app = server.make_app()
    server.start_periodic_functions(close_idle_after=3600.0)

    app.listen(args.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
