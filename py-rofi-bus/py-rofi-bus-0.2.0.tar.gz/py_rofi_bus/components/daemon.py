# pylint:disable=W,C,R
from __future__ import print_function

from os import (
    chdir,
    dup2,
    fork,
    remove,
    setsid,
    umask,
)
from sys import (
    exit as sys_exit,
    stderr,
    stdin,
    stdout,
)

from py_rofi_bus.components.mixins import HasPid


class Daemon(HasPid):

    def __init__(self, *args, **kwargs):
        HasPid.__init__(self, *args, **kwargs)

    @staticmethod
    def fork():
        try:
            pid = fork()
            if pid > 0:
                sys_exit(0)
        except OSError as error:
            print("Fork failed: ({}) {}".format(error.errno, error.strerror))
            sys_exit(1)

    @staticmethod
    def decouple_from_environment():
        chdir('/')
        umask(0)
        setsid()

    @staticmethod
    def redirect_file_descriptors(
            daemon_stdin='/dev/null',
            daemon_stdout='/dev/null',
            daemon_stderr='/dev/null',
    ):
        for file_descriptor in [stdout, stderr]:
            file_descriptor.flush()
        new_stdin = open(daemon_stdin, 'r')
        new_stdout = open(daemon_stdout, 'a+')
        new_stderr = open(daemon_stderr, 'a+')
        dup2(new_stdin.fileno(), stdin.fileno())
        dup2(new_stdout.fileno(), stdout.fileno())
        dup2(new_stderr.fileno(), stderr.fileno())

    def daemonize(
            self,
            daemon_stdin='/dev/null',
            daemon_stdout='/dev/null',
            daemon_stderr='/dev/null'
    ):
        """
        https://web.archive.org/web/20130117060508/http://onlamp.com/python/pythoncook2/solution.csp?day=1
        """
        self.fork()
        self.decouple_from_environment()
        self.fork()
        self.redirect_file_descriptors(
            daemon_stdin,
            daemon_stdout,
            daemon_stderr,
        )
        self.write_pid_file()

    def main(self):
        """Overridden by children"""

    @classmethod
    def bootstrap(cls, *args, **kwargs):
        daemon = cls(*args, **kwargs)
        daemon.daemonize('/dev/null', '/tmp/daemon.log', '/tmp/daemon.log')
        daemon.main()

if '__main__' == __name__:
    Daemon.bootstrap()
