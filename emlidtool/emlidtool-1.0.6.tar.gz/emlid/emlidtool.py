import argparse
import collections
import logging
import coloredlogs
import sys
import re
import subprocess as sub

from termcolor import colored
from emlid.ardupilot.ardupilot import ArdupilotConfigurator
from emlid.devicefactory import DeviceFactory
from emlid.deviceinfo import DeviceInformation, NotVersionControlledOSReleaseException
from emlid.devices.tester import Tester
from emlid.rcio.updater import FirmwareUpdater
from emlid.rcio.versionchecker import VersionChecker as FirmwareVersionChecker, CrcNotFoundError,\
    InappropriateFirmwareError
from emlid.util.util import ardupilot_should_not_run, ArdupilotIsRunningException,\
    NotRootException, FailingTestException, UpdateNeededException, handle_root_exception, \
    root_should_execute, UpdateError, edge_board_should_be_used
from emlid.ui.mainwindow import MainWindow


coloredlogs.install(stream=sys.stdout)


@root_should_execute
def do_ardupilot(args):
    if args.action == 'configure':
        if args.no_tui:
            try:
                device_information = get_device_information()
            except NotVersionControlledOSReleaseException as e:
                logging.warning(str(e))
            else:
                configurator = ArdupilotConfigurator(device_information.product)
                try:
                    configuration = configurator.get_configuration()
                    output = configurator.configure(configuration)
                    print(colored(output, 'green'))
                except NotRootException:
                    handle_root_exception()
        else:
            main_window = MainWindow()
            main_window.run()
    elif args.action == 'help':
        print(sys.argv[0])
        with open("/etc/motd") as motd:
            print(motd.read())
    else:
        print(colored("\nInvalid argument. Please, try again\n", "yellow"))
        sys.exit(1)


def do_info(args=''):
    try:
        information = get_device_information()
    except NotVersionControlledOSReleaseException as e:
        logging.warning(str(e))
    else:
        print(information)


def check_rcio(args):
    if args.p:
        checker = FirmwareVersionChecker(firmware_path=args.p)
    else:
        checker = FirmwareVersionChecker()
    try:
        if args.l:
            update_needed = checker.check(long_output=True)
        else:
            update_needed = checker.check(long_output=False)
    except CrcNotFoundError as e:
        print(e)
        exit(1)
    except InappropriateFirmwareError as e:
        print(e)
        exit(1)

    if update_needed:
        raise UpdateNeededException


@root_should_execute
def update_rcio(args):
    try:
        if args.p:
            updater = FirmwareUpdater(args.p, verbose_update=args.v)
        else:
            updater = FirmwareUpdater(verbose_update=args.v)
    except NotRootException:
        handle_root_exception()
    try:
        updater.update(quiet_update=args.q, force_update=args.f)
    except UpdateError as e:
        print(colored(e, 'red'))
        exit(1)
    except InappropriateFirmwareError as e:
        print(colored(e, 'red'))
        exit(1)


def restart_rcio(args):
    updater = FirmwareUpdater()
    try:
        updater.restart()
    except UpdateError as e:
        print(colored(e, 'red'))

@ardupilot_should_not_run
def do_tests(args):
    try:
        information = get_device_information()
    except NotVersionControlledOSReleaseException as e:
        logging.exception(str(e))

    device = get_device(information)
    tester = Tester(device)
    results = tester.run_tests(args.sensors)

    all_tests_passed = True
    for name, result in results.items():
        if result.result:
            logging.info("{}: Passed".format(name))
        else:
            if 'sudo' in result.description:
                logging.warning("{}: Warning\n -- Reason: {}".format(name, result.description))
            logging.error("{}: Failed\n -- Reason: {}".format(name, result.description))
            all_tests_passed = False

    if all_tests_passed:
        return
    else:
        raise FailingTestException


def get_device(information):
    return DeviceFactory(information).create()


def get_device_information():
    return DeviceInformation()


def show_version():
    import pkg_resources
    try:
        version = pkg_resources.require("emlidtool")[0].version
        print("emlidtool version: " + version)
    except pkg_resources.DistributionNotFound:
        print("Tool not installed systemwide!")


@edge_board_should_be_used
def show_status_of_edge_services(args=''):
    services = {
        'ardupilot-wrapper',
        'mavlink-router',
        'csd',
        'acd',
        'wmd',
        'uavcannodeallocator',
        'selftests'
    }

    print(colored("Getting information about services", 'yellow'))

    for service in services:
        info_message = colored("{} status".format(service), 'blue')
        print("{} : {}".format(info_message, service_status_information(service)))

    print(colored("rcio updater", 'blue') + " : ", end="")
    FirmwareVersionChecker().check(long_output=False)


def service_status_information(service):
    try:
        command = 'systemctl status {}'.format(service)
        proc = sub.Popen(command, shell=True, stdout=sub.PIPE)
        service_info = proc.communicate()[0].decode('utf-8')

        return "{}, {}".format(get_current_status(service_info), get_boot_start_status(service_info))

    except (sub.CalledProcessError, AttributeError):
        return colored("FAILED: can't get status", 'red')


def get_current_status(service_info):
    current_status = re.search(r'(?<=Active: ).+\)', service_info).group(0)
    is_active = current_status.split()[0] == "active"
    return colored(current_status, 'green') if is_active \
        else colored(current_status, 'magenta')


def get_boot_start_status(service_info):
    boot_start_status = re.search(r'(?<=; )\w+;', service_info).group(0)
    return colored(boot_start_status, 'cyan') if boot_start_status == "enabled;" \
        else colored(boot_start_status, 'yellow')


class Emlidtool:

    help = {
        'emlidtool': 'Utility to make your experience with autopilot easier',
        'info': 'Information about the system',
        'test': 'Run simple tests on the device',
        'ardupilot': 'Ardupilot related stuff',
        'rcio': 'Tool to configure RCIO',
        'update': 'Tool to update firmware',
        'restart': 'Tool to restart firmware',
        'check': 'Tool to check firmware',
        'check_long': 'Show additional info',
        'version': 'Version information',
        'update_yes': 'Yes on all questions',
        'verbose_update': 'Verbose update',
        'update_quiet': 'No stdout',
        'update_force': 'Force update',
        'update_path': 'Specify firmware path',
        'check_path': 'Specify firmware path to check',
        'status' : 'Information about status services'
    }

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description=self.help['emlidtool'],
            usage='emlidtool <command> [<args>]',
            formatter_class=argparse.RawTextHelpFormatter)

        self.parser.add_argument('command', default='test', nargs='?',
                                 choices=('info', 'test', 'rcio', 'ardupilot', 'status'))
        self.parser.add_argument('info', action='store_true', help=self.help['info'])
        self.parser.add_argument('rcio', action='store_true', help=self.help['rcio'])
        self.parser.add_argument('test', action='store_true', help=self.help['test'])
        self.parser.add_argument('ardupilot', action='store_true', help=self.help['ardupilot'])
        self.parser.add_argument('status', action='store_true', help=self.help['status'])
        self.parser.add_argument('-v', '--version', action='store_true', help=self.help['version'])

    def parse_args(self):
        args = self.parser.parse_args(sys.argv[1:2])

        if args.version:
            show_version()
            exit(0)

        if not hasattr(self, args.command):
            print('Unrecognized command')
            self.parser.print_help()
            exit(1)
        try:
            getattr(self, args.command)()
        except NotRootException:
            handle_root_exception()

    def info(self):
        info = argparse.ArgumentParser(description=self.help['info'])
        info.set_defaults(func=do_info)
        args = info.parse_args(sys.argv[2:])
        self.func(info, args)

    def test(self):
        tests = argparse.ArgumentParser(description=self.help['test'])
        tests.add_argument('sensors', default='all', nargs='*',
                           action='store', help='Sensor to test')
        tests.set_defaults(func=do_tests)
        args = tests.parse_args(sys.argv[2:])
        self.func(tests, args)

    def ardupilot(self):
        ardupilot = argparse.ArgumentParser(description=self.help['ardupilot'])
        ardupilot.add_argument('action', default='configure', nargs='?',
                               action='store', help='{help, configure}')
        ardupilot.add_argument('--no-tui', action='store_true')
        ardupilot.set_defaults(func=do_ardupilot)
        args = ardupilot.parse_args(sys.argv[2:])
        self.func(ardupilot, args)

    def rcio(self):
        rcio = argparse.ArgumentParser(description=self.help['rcio'],
                                       usage='emlidtool rcio [<args>]')
        subparser_rcio = rcio.add_subparsers()

        check = subparser_rcio.add_parser('check', description=self.help['check'],
                                          usage='emlidtool rcio check [-l]',
                                          help=self.help['check'])

        check.add_argument('-l', action='store_true', help=self.help['check_long'])
        check.add_argument('-p', nargs='?', help=self.help['check_path'])
        check.set_defaults(func=check_rcio)

        update = subparser_rcio.add_parser('update', description=self.help['update'],
                                           usage='emlidtool rcio update [-f][-y][-q]',
                                           help=self.help['update'])
        update.add_argument('-f', action='store_true', help=self.help['update_force'])
        update.add_argument('-y', action='store_true', help=self.help['update_yes'])
        update.add_argument('-q', action='store_true', help=self.help['update_quiet'])
        update.add_argument('-v', action='store_true', help=self.help['verbose_update'])
        update.add_argument('-p', nargs='?', help=self.help['update_path'])
        update.set_defaults(func=update_rcio)

        restart = subparser_rcio.add_parser('restart', description=self.help['restart'],
                                           usage='emlidtool rcio restart',
                                           help=self.help['restart'])
        restart.set_defaults(func=restart_rcio)
        args = rcio.parse_args(sys.argv[2:])
        self.func(rcio, args)

    def status(self):
        status = argparse.ArgumentParser(description=self.help['status'])
        status.set_defaults(func=show_status_of_edge_services)
        args = status.parse_args(sys.argv[2:])
        self.func(status, args)

    @staticmethod
    def func(parser, args):
        try:
            args.func(args)
        except AttributeError:
            parser.print_help()


def main():
    if len(sys.argv) == 1:
        show_version()
        do_info()
        FakeTestArg = collections.namedtuple('FakeTestArg', ['sensors'])

        try:
            do_tests(FakeTestArg(sensors='all'))
        except ArdupilotIsRunningException:
            logging.warning("Could not run tests because ArduPilot is running")
        except FailingTestException:
            exit(1)
        print('emlidtool -h to get more help')
        sys.exit(0)
    else:
        emlidtool = Emlidtool()
        try:
            emlidtool.parse_args()
        except FailingTestException:
            exit(1)
        except UpdateNeededException:
            exit(2)


if __name__ == "__main__":
    main()
