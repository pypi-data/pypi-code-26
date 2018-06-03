# pylint:disable=W,C,R

from argparse import ArgumentParser
from sys import argv
from subprocess import check_call

from gi.repository.GLib import Error as GlibError
from pydbus import SessionBus

BUS = SessionBus()
try:
    DAEMON = BUS.get("pro.wizardsoftheweb.pyrofibus.daemon")
except Exception:  # pylint:disable=catching-non-exception
    DAEMON = None


def start():
    check_call(['python', '-m', 'py_rofi_bus.main_dbus_daemon'])


def stop():
    if DAEMON is None:
        print('Daemon not running')
    else:
        print('Stopping daemon')
        DAEMON.stop()


def status():
    if DAEMON is None:
        print('Daemon not running')
    else:
        print("Daemon running: {}".format(DAEMON.is_running()))


class Daemon(object):

    ACTIONS = {
        'stop': stop,
        'start': start,
        'status': status,
    }

    def __init__(self, parent_parser=None):
        if parent_parser is None:
            self.parser = ArgumentParser(
                prog='daemon',
                description='Manage the py-rofi-bus daemon'
            )
        else:
            self.parser = parent_parser.add_parser(
                'daemon',
                help='Manage the py-rofi-bus daemon'
            )

    def attach_subparsers(self):
        self.subparsers = self.parser.add_subparsers(
            dest='action',
            help='Available actions',
        )

    def add_action_start(self):
        self.action = self.subparsers.add_parser(
            'start',
            help='Start the daemon',
        )

    def add_action_stop(self):
        self.action = self.subparsers.add_parser(
            'stop',
            help='Stop the daemon',
        )

    def add_action_status(self):
        self.action = self.subparsers.add_parser(
            'status',
            help='Check the status of the daemon',
        )

    @staticmethod
    def bootstrap(args=None):
        if args is None:
            args = argv[1:]
        daemon = Daemon()
        daemon.attach_subparsers()
        daemon.add_action_start()
        daemon.add_action_status()
        daemon.add_action_stop()
        config = daemon.parser.parse_args(args)
        Daemon.ACTIONS[config.action]()

if '__main__' == __name__:
    Daemon.bootstrap()
