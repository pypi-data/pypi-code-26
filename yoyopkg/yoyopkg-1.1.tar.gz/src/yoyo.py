import sys

import argparse

from src.core.Yoyo import Yoyo


def arg_parse():
    parser = argparse.ArgumentParser(description='Yoyo module manager')

    parser.add_argument("mode", help="Mode", choices=['install', 'remove', 'update', 'list', 'details', 'verify'])
    parser.add_argument('package', nargs='?')
    parser.add_argument('--local', '-l', action="store_true")
    parser.add_argument('--force', '-f', action="store_true")
    parser.add_argument('--nocache', '-nc', action="store_true")

    return parser.parse_args()

#yoyo storeadd STOREPATH
#yoyo pathadd STORENAME PATH

def run(scriptPath):
    args = arg_parse()

    yoyo = Yoyo(scriptPath, args.local, args.force, args.nocache, args.mode != 'update')


    if args.mode in ['install', 'remove']:
        if args.package is None:
            print('Error package name need to be specified')
            return False

        return getattr(yoyo, args.mode)(args.package)

    if args.mode == 'update':
        yoyo.installOptions.isUpdateCmd = True
        if args.package is not None:
            print('Error update take no argument (for now, then store name can be specified)')
            return False

        return yoyo.update()

    if args.mode == 'list':
        if args.package is not None:
            print('Error list take no argument')
            return False
        return yoyo.printAllModules()

    if args.mode == 'details':
        if args.package is not None:
            print('Error details take no argument')
            return False
        return yoyo.printDetails()

    if args.mode == 'verify':
        return yoyo.verify(args.package)

    print('Not yet implemented')
    return False


if __name__ == '__main__':
    import os
    try:
        run(os.path.realpath(__file__))
    except KeyboardInterrupt:
        sys.exit(0)
