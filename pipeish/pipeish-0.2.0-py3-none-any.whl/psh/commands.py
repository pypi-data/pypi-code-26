# vim: set ts=2 sw=2 st=2 et:


import shlex
from subprocess import PIPE, Popen


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

    def __call__(self):
        ''' execute command.
            should change self.code after command execution
        '''

        if self.code is not None:
            raise AlreadyCalled(self.command_line)

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

    def __call__(self):
        super().__call__()

        try:
            stdin = self.stdin
            p = Popen(self._args,
                      shell=False,
                      universal_newlines=True,
                      stdin=PIPE,
                      stdout=PIPE, stderr=PIPE)
            self.stdout, self.stderr = p \
                .communicate(input=stdin, timeout=self._timeout)
        except StdinMissing:
            p = Popen(self._args,
                      shell=False,
                      universal_newlines=True,
                      stdout=PIPE, stderr=PIPE)

            self.stdout, self.stderr = p \
                .communicate(timeout=self._timeout)

        self.code = p.returncode

        return self

    def __or__(self, other):
        ''' works like 'set -o pipefail' by default '''

        try:
            self()
        except AlreadyCalled:
            pass

        if self:
            other.stdin = self.stdout
            return other()
        else:
            return self
