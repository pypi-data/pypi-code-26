import os
import re
import argparse
import configparser

import dotme

from .link import Link
from .target import Target
from .utils import RC_FILE, RC_CONFIG, GENERIC_DIR, CONFIG_YML, PROFILE_NAME


def parser_init(parser: argparse.ArgumentParser):
    parser.add_argument('-v', '--version', action='store_true', help='Show version')

    subparsers = parser.add_subparsers(title='sub commands', dest='sub_cmd')

    subparser_init = subparsers.add_parser('init', description='Init a empty dotfiles repo')

    subparser_list = subparsers.add_parser('list', description='List')
    subparser_list.add_argument('-t', '--target', nargs='?', default=None)
    subparser_list.add_argument('bundle', nargs='*', default=None)
    subparser_list.add_argument('-a', '--all', action='store_true', help='List all')

    subparser_deploy = subparsers.add_parser('deploy', description='Deploy target dotfiles')
    subparser_deploy.add_argument('-t', '--target', nargs='?', default=None)
    subparser_deploy.add_argument('bundle', nargs='*', default=None)
    subparser_deploy.add_argument('-f', '--force', action='store_true', help='Force deploying if dst exists, old dst will be backed up')
    subparser_deploy.add_argument('-c', '--clean', action='store_true', help='Do not backup')

    subparser_collect = subparsers.add_parser('collect', description='Collect target dotfiles')
    subparser_collect.add_argument('-t', '--target', nargs='?', default=None)
    subparser_collect.add_argument('bundle', nargs='*', default=None)
    subparser_collect.add_argument('-f', '--force', action='store_true', help='Force collecting if src exists, old src will be backed up')
    subparser_collect.add_argument('-c', '--clean', action='store_true', help='Do not backup')


def main():
    home = os.path.expanduser('~')
    # rc_path = os.path.join(home, RC_FILE)
    rc_path = os.path.join(home, '/Users/xinhangliu/workspace/dotme/test/host/.dotmerc')

    base = RC_CONFIG['default']['base']
    hostname = RC_CONFIG['default']['hostname']
    username = RC_CONFIG['default']['username']

    if os.path.exists(rc_path):
        rc = configparser.ConfigParser()
        rc.read(rc_path)
        if rc.get('DEFAULT', 'base'):
            base = rc.get('DEFAULT', 'base')
        if rc.get('DEFAULT', 'hostname'):
            hostname = rc.get('DEFAULT', 'hostname')
        if rc.get('DEFAULT', 'username') != '':
            username = rc.get('DEFAULT', 'username')

    def init_handler():
        if os.path.exists(base):
            print('Folder already exists: %s' % base)
            exit(1)

        user_dotfiles_home = os.path.join(base, hostname, username)
        os.makedirs(user_dotfiles_home)
        os.makedirs(os.path.join(base, GENERIC_DIR))
        with open(os.path.join(user_dotfiles_home, PROFILE_NAME), 'w') as f:
            f.write(CONFIG_YML)

    def list_handler(target, bundle, all):
        if target is None:
            target = (hostname, username)
        else:
            match = re.match('^([\w\d_-]+)/([\w\d_-]+)$', target)
            if match:
                target = match.groups()
            else:
                print('TARGET is not valid: %s. Should in this form \'hostname/username\'' % target)
                exit(1)

        if not os.path.exists(os.path.join(base, *target)):
            print('TARGET does not exist: %s' % '/'.join(target))
            exit(1)

        t = Target(base, *target)

        if not t.profile.bundles:
            print('No bundles to link')
            exit(0)
        if not bundle:
            print('List ALL bundles ...')
            for key, value in t.profile.bundles.items():
                print(key)
                if all:
                    for ln in value['links']:
                        ln = Link(t.get_bundle_home(value), ln)
                        print('[%s]----[%s]----[%s]' % (ln.status[0].value, ln.connection.value, ln.status[1].value))

        for key in bundle:
            b = t.profile.bundles.get(key)
            if b:
                print(key)
                print(t.get_link_names(b))
            else:
                print('bundle does not exit: %s' % key)
                exit(1)

    def deploy_handler(target, bundle, force, clean):
        if target is None:
            target = (hostname, username)
        else:
            match = re.match('^([\w\d_-]+)/([\w\d_-]+)$', target)
            if match:
                target = match.groups()
            else:
                print('TARGET is not valid: %s. Should in this form \'hostname/username\'' % target)
                exit(1)

        if not os.path.exists(os.path.join(base, *target)):
            print('TARGET does not exist: %s' % '/'.join(target))
            exit(1)

        t = Target(base, *target)

        if not t.profile.bundles:
            print('No bundles to link')
            exit(0)
        if not bundle:
            print('Linking ALL bundles ...')
            for key, value in t.profile.bundles.items():
                print(key)
                status = t.deploy_bundle(value, force)
                print(status)

        for key in bundle:
            b = t.profile.bundles.get(key)
            if b:
                status = t.deploy_bundle(b, force)
                print(status)
            else:
                print('bundle does not exit: %s' % key)
                exit(1)

    def collect_handler(target, bundle, force, clean):
        if target is None:
            target = (hostname, username)
        else:
            match = re.match('^([\w\d_-]+)/([\w\d_-]+)$', target)
            if match:
                target = match.groups()
            else:
                print('TARGET is not valid: %s. Should in this form \'hostname/username\'' % target)
                exit(1)

        if not os.path.exists(os.path.join(base, *target)):
            print('TARGET does not exist: %s' % '/'.join(target))
            exit(1)

        t = Target(base, *target)

        if not t.profile.bundles:
            print('No bundles to collect')
            exit(0)
        if not bundle:
            print('Collecting ALL bundles ...')
            for key, value in t.profile.bundles.items():
                print(key)
                status = t.collect_bundle(value, force)
                print(status)

        for key in bundle:
            b = t.profile.bundles.get(key)
            if b:
                status = t.collect_bundle(b, force)
                print(status)
            else:
                print('bundle does not exit: %s' % key)
                exit(1)

    parser = argparse.ArgumentParser()
    parser_init(parser)
    args = parser.parse_args()
    print(args)

    # dotme = Dotme(base, hostname, username)

    if args.version:
        print('Dotme %s' % dotme.__version__)

    if args.sub_cmd == 'init':
        init_handler()
    elif args.sub_cmd == 'list':
        list_handler(args.target, args.bundle, args.all)
    elif args.sub_cmd == 'deploy':
        deploy_handler(args.target, args.bundle, args.force, args.clean)
    elif args.sub_cmd == 'collect':
        collect_handler(args.target, args.bundle, args.force, args.clean)
