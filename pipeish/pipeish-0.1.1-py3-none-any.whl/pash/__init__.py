# vim: set ts=2 sw=2 st=2 et:

# TODO:
# - create github repo
# - exec with subprocess
# - redirect > to file and /dev/null
# - redirect >> to file and /dev/null
# - handle commands with params
# - stub not implemented operators
# - override truth (__bool__) based on return code (nonzero == False)
# - implement 'pipefail' somehow.
#       maybe with `|=` (__ior__)
#       _('ls') | _('grep') |= ('xargs')
#       if `grep` fails, whole chain will fail and xargs will not be executed
# - maybe pipe by default should work in `pipefail` mode, and __ior__ override it
# - redirect stdout and stderror
# - write tests
# - create package to install with pip
# - emulate `set -e` and/or `set -o pipefail`
#
# Links:
# https://docs.python.org/3.6/library/operator.html
# https://docs.python.org/3/library/subprocess.html
#
# Examples:
# pattern = 'Pip'
# (_('ls') | _(f'grep {pattern}')).stdout

import shlex
from subprocess import Popen, PIPE


class AbsCommand():

    command_line = None

    stdin = None
    stdout = None
    stderr = None
    code = None

    def __call__(self):
        ''' execute command '''
        raise NotImplemented()

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
        return self.code == 0

    # def __repr__(self):
    #     raise NotImplemented('not decided what should go there just yet')

    # def __str__(self):
    #     raise NotImplemented('not decided what should go there just yet')


class Command(AbsCommand):

    _args = None
    _timeout = 0

    def __init__(self, cmd, timeout=1):
        self.command_line = cmd
        self._args = shlex.split(cmd)
        self._timeout = timeout

    def __call__(self):
        if self.stdin:
            p = Popen(self._args,
                      shell=False,
                      universal_newlines=True,
                      stdin=PIPE,
                      stdout=PIPE, stderr=PIPE)
        else:
            p = Popen(self._args,
                      shell=False,
                      universal_newlines=True,
                      stdout=PIPE, stderr=PIPE)


        # import pudb; pudb.set_trace()

        if self.stdin:
            self.stdout, self.stderr = p \
                .communicate(input=self.stdin, timeout=self._timeout)
        else:
            self.stdout, self.stderr = p \
                .communicate(timeout=self._timeout)

        self.code = p.returncode



        # self.stdout = p.stdout
        # self.stderr = p.stderr
        # self.code = p.returncode



        # self.stdout = f'Std out string from {self.command}'
        # self.stderr = f'Std err string from {self.command}'
        # self.code = 22
        return self

    def __or__(self, other):
        # import pudb; pudb.set_trace()

        self()

        other.stdin = self.stdout
        return other()

    # def __str__(self):
    #     r = self.stderr
    #     if self.stdout:
    #         r += self.stdout
    #     return r

    # __repr__ = __str__
