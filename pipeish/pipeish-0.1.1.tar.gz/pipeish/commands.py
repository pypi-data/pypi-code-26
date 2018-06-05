# vim: set ts=2 sw=2 st=2 et:


import shlex
from subprocess import PIPE, STDOUT, Popen
import subprocess


class BaseCommandException(Exception):
    pass


class AlreadyCalled(BaseCommandException):
    pass


class NeverCalled(BaseCommandException):
    pass


class StdinMissing(BaseCommandException):
    pass


class StdoutMissing(BaseCommandException):
    pass


class StderrMissing(BaseCommandException):
    pass


class BaseCommand():

    command_line = None

    _stdin = None
    _stdout = None
    _stderr = None

    code = None

    def __or__(self, other):
        ''' | '''
        raise NotImplemented()

    def __gt__(self, other):
        ''' > '''
        raise NotImplemented()

    def __rshift__(self, other):
        ''' >> '''
        raise NotImplemented()

    def __bool__(self):
        if self.code is None:
            raise NeverCalled(self.command_line)
        return self.code == 0

    def __str__(self):
        try:
            if len(self.stderr) > 0:
                return self.stderr
            else:
                return self.stdout
        except StderrMissing:
            return self.stdout

    @property
    def stdin(self):
        if self._stdin is None:
            raise StdinMissing(self.command_line)
        return self._stdin

    @stdin.setter
    def stdin(self, value):
        self._stdin = value

    @property
    def stdout(self):
        if self._stdout is None:
            raise StdoutMissing(self.command_line)
        return self._stdout

    @stdout.setter
    def stdout(self, value):
        self._stdout = value

    @property
    def stderr(self):
        if self._stderr is None:
            raise StderrMissing(self.command_line)
        return self._stderr

    @stderr.setter
    def stderr(self, value):
        self._stderr = value


class Command(BaseCommand):

    _args = None
    _timeout = 0

    def __init__(self, cmd, timeout=1):
        self.command_line = cmd
        self._args = shlex.split(cmd)
        self._timeout = timeout

    def _raise_if_was_called(self):
        if self.code is not None:
            raise AlreadyCalled(self.command_line)

    def _exec_silent(self):
        self._raise_if_was_called()

        # XXX make distinction based on stdin more visible in code
        try:
            stdin = self.stdin
            p = Popen(self._args,
                      stdin=PIPE,
                      stdout=PIPE, stderr=PIPE,
                      shell=False,
                      universal_newlines=True,
                      )
            self.stdout, self.stderr = p \
                .communicate(input=stdin, timeout=self._timeout)
        except StdinMissing:
            p = Popen(self._args,
                      stdout=PIPE, stderr=PIPE,
                      shell=False,
                      universal_newlines=True,
                      )

            self.stdout, self.stderr = p \
                .communicate(timeout=self._timeout)

        self.code = p.returncode
        return self

    def _exec(self):
        self._raise_if_was_called()

        p = subprocess.run(self._args,
                           stderr=STDOUT,
                           shell=False,
                           universal_newlines=True,
                           check=True,
                           )

        self.code = p.returncode
        return self

    def __call__(self):
        self._exec()

    def __or__(self, other):
        ''' works like 'set -o pipefail' by default '''

        try:
            self._exec_silent()
        except AlreadyCalled:
            pass

        if self:
            other.stdin = self.stdout
            return other._exec_silent()
        else:
            return self
