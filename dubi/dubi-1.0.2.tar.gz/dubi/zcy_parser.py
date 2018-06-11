import argparse

from zcy_action import *

parser = argparse.ArgumentParser(prog='dubi', description='Dubbo Invoke Tool',
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog='Enjoy it!\nEmail: liangchenhao@cai-inc.com')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0')
parser.add_argument('-e', '--env', nargs=0, action=ShowEnvAction, help='show the available environment and exit')
parser.add_argument('-pv', '--provider_version', nargs=1, action=ProviderVersionAction,
                    help='specify the version of provider if only one service matched (e.g., -pv 1.0.0)')
parser.add_argument('-pr', '--provider_random', nargs=0, action=ProviderRandomAction,
                    help='chose provider random if only one service matched')
parser.add_argument('-t', '--telnet', nargs=0, action=DoTelnetAction,
                    help='telnet provider if only one provider matched')
parser.add_argument('-i', '--invoke', nargs=2, action=InvokeAction,
                    help='invoke the provider with method info given if only one provider matched (e.g., -i fun ())')
parser.add_argument('arg', nargs='+', action=EnvAction, help='env [app] [service] (ignore case match)')
