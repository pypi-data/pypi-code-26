import os
import sys
import signal
import subprocess as sub
from termcolor import colored


class UpdateNeededException(Exception):
    pass


class FailingTestException(Exception):
    pass


class UpdateTimeoutError(Exception):
    pass


class UpdateError(Exception):
    pass


class NotRootException(Exception):
    pass


class ArdupilotIsRunningException(Exception):
    pass


def root_should_execute(fn):
    def wrapped(*args, **kwargs):
        if os.getuid() != 0:
            raise NotRootException()
        else:
            return fn(*args, **kwargs)
    return wrapped


def timeout(seconds):
    def real_timeout(fn):
        def wrapped(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            fn(*args, **kwargs)
            signal.alarm(0)
            return fn(*args, **kwargs)
        return wrapped
    return real_timeout


def timeout_handler(signum, frame):
    raise UpdateTimeoutError


def handle_root_exception():
    sys.stderr.write('Please, try again with sudo\n')
    sys.stderr.write('usage: sudo emlidtool {}\n'.format(' '.join(sys.argv[1:])))
    sys.exit(1)


def ardupilot_should_not_run(fn):
    def wrapped(*args, **kwargs):
        try:
            sub.check_call(["! ps -AT | grep -q -o ap-timer"], shell=True)
        except sub.CalledProcessError:
            raise ArdupilotIsRunningException

        fn(*args, **kwargs)
    return wrapped


def edge_board_should_be_used(fn):
    def wrapped(*args, **kwargs):
        if os.path.exists("/edge"):
            fn(*args, **kwargs)
        else:
            print("Please, use Edge board for this command")
    return wrapped
