"""
Main module for hostblock command line utility.
"""
import argcomplete
import argparse
import errno
import json
import os
import re
import subprocess
import sys
import textwrap
import hostblock

global config_path

class BlockedHosts(set):
    '''Extensible set of hosts.'''

    def __init__(self, hosts = set(), redirect = '0.0.0.0'):
        self.redirect = redirect
        self.update(set(hosts))
        super()

    def __iter__(self):
        ordered_hosts = list(set(self))
        ordered_hosts.sort()
        for x in ordered_hosts:
            yield x
        
    def __repr__(self):
        return "BlockedHosts('{}', {})".format(set(self), self.redirect)

    def __str__(self):
        return '\n'.join(list(self))

    def __add__(self, other):
        return BlockedHosts(set(self).union(set(other)), self.redirect)

    def __iadd__(self, other):
        self.update(set(other))
        return self

    def __sub__(self, other):
        return BlockedHosts(set(self).difference(set(other)), self.redirect)

    def __isub__(self, other):
        self.difference_update(set(other))
        return self
        
    def blockstring(self):
        delimiter = '\n{} '.format(self.redirect)
        return self.redirect + ' ' + delimiter.join(list(self))


def __parse_args():
    """Parse command line arguments and return an argparse object."""
    parser = argparse.ArgumentParser(
        prog = "hostblock",
        description="Add hosts file entries to block unwanted hosts.",
        )
    parser.add_argument(
        "-v", "--version", action="store_true",
        help="Show version info and exit."
        )
    parser.add_argument(
        "--config", "-c", action="store", type=str,
        help='''Specify config file path. Defaults to '~/.hostblock'.'''
        )
    parser.add_argument(
        "--hosts-file", action="store", type=str,
        help='''Specify hosts file path. Defaults to '/etc/hosts'.'''
        )
    subparsers = parser.add_subparsers(
        description="(use each command with -h for more help)",
        dest="cmd",
        )
    parser.set_defaults(
        config=os.path.expanduser('~/.hostblock'),
        hosts_file = '/etc/hosts',
        )

    parser_ab = subparsers.add_parser(
        "ab",
        description='''Add host(s) to local blacklist.''',
        )
    parser_rb = subparsers.add_parser(
        "rb",
        description='''Remove host(s) from local blacklist.''',
        )
    parser_eb = subparsers.add_parser(
        "eb",
        description='''Empty local blacklist.''',
        )
    parser_lb = subparsers.add_parser(
        "lb",
        description='''List all hosts from local blacklist.''',
        )
    parser_aw = subparsers.add_parser(
        "aw",
        description='''Add host(s) to local whitelist.''',
        )
    parser_rw = subparsers.add_parser(
        "rw",
        description='''Remove host(s) from local whitelist.''',
        )
    parser_ew = subparsers.add_parser(
        "ew",
        description='''Empty local whitelist.''',
        )
    parser_lw = subparsers.add_parser(
        "lw",
        description='''List all hosts from local whitelist.''',
        )
    parser_list = subparsers.add_parser(
        "list", aliases=["l"],
        description='''List all hosts that will be blocked.''',
        )
    parser_count = subparsers.add_parser(
        "count", aliases=["c"],
        description='''Count all hosts in blacklist and whitelist.''',
        )
    parser_apply = subparsers.add_parser(
        "apply",
        description='''Apply blocked hosts to your hosts file.''',
        )
    def url_type(s, pat=re.compile(r"^\s*(https?://)?(([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]*\.[a-zA-Z0-9][a-zA-Z0-9-_]*\.?)([/#?\s].*)?$")):
        domain = pat.match(s)
        if domain is None:
            raise argparse.ArgumentTypeError(
                "Not a valid domain or URL '{}'.".format(s))
        return domain.group(2)
    for subparser in [ parser_ab, parser_rb, parser_aw, parser_rw ]:
        subparser.add_argument(
            dest='hosts', metavar='host', type=url_type, nargs='+',
            help='''Hostname to add/remove from local blacklist/whitelist.
                Any valid URL strings are accepted.''',
            )
    for subparser in [
            parser_list, parser_count, parser_apply, parser_lb, parser_lw]:
        subparser.add_argument(
            dest='configs', metavar='config', nargs='*', type=str,
            help='''Optional list of config files to use. If not provided,
                default config or the one defined with --config will be used
                only. This option overrides the --config option.''',
            )

    argcomplete.autocomplete(parser)
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    return parser.parse_args()

def require_sudo(func):
    '''Call same script again with sudo and pass existing confing argument.'''
    def wrapper(*args, **kwargs):
        if os.geteuid() == 0:
            func(*args, **kwargs)
        else:
            print("Acquiring sudo permission.")
            script = sys.argv[0]
            rest_args = sys.argv[1:]
            config = config_path
            sp = subprocess.Popen(
                ['sudo', 'python3', script, '--config', config, *rest_args])
            sp.communicate()
            sys.exit(sp.returncode)
    return wrapper

@require_sudo
def update_hosts_file(hosts_file:str, blocked_hosts:BlockedHosts):
    host_re = re.compile(
        '^\s*({})\s.*$'.format(re.escape(blocked_hosts.redirect)))
    existing_no_block_lines = ''
    with open(hosts_file) as f:
        for line in f.readlines():
            found_host = host_re.match(line)
            if found_host is None:
                existing_no_block_lines += line
    with open(hosts_file, 'w') as f:
        print('Updating ' + hosts_file)
        f.write(existing_no_block_lines + blocked_hosts.blockstring())

def init_local_config(config):
    if not os.path.isfile(config):
        conf = {}
        conf['blacklist'] = []
        conf['whitelist'] = []
        with open(config, 'w') as f:
            f.write(json.dumps(conf))

def read_hosts(config):
    # return 2 sets of hosts: blacklist, whitelist
    init_local_config(config)
    conf = {}
    with open(config) as f:
        conf = json.loads(f.read())
    return BlockedHosts(conf['blacklist']), BlockedHosts(conf['whitelist'])

def read_hosts_multy_configs(configs):
    black, white = BlockedHosts(), BlockedHosts()
    for config in configs:
        another_black, another_white = read_hosts(config)
        black += another_black
        white += another_white
    return black, white

def write_hosts(blacklist:BlockedHosts, whitelist:BlockedHosts, config):
    conf = {}
    conf['blacklist'] = list(blacklist)
    conf['whitelist'] = list(whitelist)
    with open(config, 'w') as f:
        f.write(json.dumps(conf))

def main():
    global config_path
    args = __parse_args()
    config_path = args.config # used only in require_sudo decorator
    
    if args.version:
        print("hostblock {} - Copyright {} {} <{}>".format(
            hostblock.__version__,
            hostblock.__year__,
            hostblock.__author__,
            hostblock.__author_email__,
            ))
        sys.exit(0)
    if args.cmd == 'ab':
        black, white = read_hosts(args.config)
        print('\n'.join(set(args.hosts) - black))
        black += args.hosts
        write_hosts(black, white, args.config)
    if args.cmd == 'rb':
        black, white = read_hosts(args.config)
        print('\n'.join(set(args.hosts) & black))
        black -= args.hosts
        write_hosts(black, white, args.config)
    if args.cmd == 'eb':
        black, white = read_hosts(args.config)
        write_hosts(BlockedHosts(), white, args.config)
    if args.cmd == 'lb':
        black, white = set(), set()
        if args.configs:
            black, white = read_hosts_multy_configs(args.configs)
        else:
            black, white = read_hosts(args.config)
        try:
            print(str(black))
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e
    if args.cmd == 'aw':
        black, white = read_hosts(args.config)
        print('\n'.join(set(args.hosts) - white))
        white += args.hosts
        write_hosts(black, white, args.config)
    if args.cmd == 'rw':
        black, white = read_hosts(args.config)
        print('\n'.join(set(args.hosts) & white))
        white -= args.hosts
        write_hosts(black, white, args.config)
    if args.cmd == 'ew':
        black, white = read_hosts(args.config)
        write_hosts(black, BlockedHosts(), args.config)
    if args.cmd == 'lw':
        black, white = set(), set()
        if args.configs:
            black, white = read_hosts_multy_configs(args.configs)
        else:
            black, white = read_hosts(args.config)
        try:
            print(str(white))
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e
    if args.cmd in ('list', 'l'):
        black, white = set(), set()
        if args.configs:
            black, white = read_hosts_multy_configs(args.configs)
        else:
            black, white = read_hosts(args.config)
        try:
            print(str(black - white))
        except IOError as e:
            if e.errno != errno.EPIPE:
                raise e
    if args.cmd in ('count', 'c'):
        black, white = set(), set()
        if args.configs:
            black, white = read_hosts_multy_configs(args.configs)
        else:
            black, white = read_hosts(args.config)
        print("blacklist: {}".format(len(black)))
        print("whitelist: {}".format(len(white)))
    if args.cmd == 'apply':
        black, white = set(), set()
        if args.configs:
            black, white = read_hosts_multy_configs(args.configs)
        else:
            black, white = read_hosts(args.config)
        if len(args.configs):
            pass
        else:
            black, white = read_hosts(args.config)
        update_hosts_file(args.hosts_file, black - white)
    sys.exit(0)

if __name__ == "__main__":
    main()


