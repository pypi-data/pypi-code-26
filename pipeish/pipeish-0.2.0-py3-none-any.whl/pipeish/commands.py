# vim: set ts=4 sw=4 st=4 et:

import shlex
from subprocess import DEVNULL, PIPE, STDOUT, Popen


class Command:

    out_pipes = {
        't': None,
        'n': DEVNULL,
        'i': PIPE,
    }
    err_pipes = {
        't': None,
        'n': DEVNULL,
        'i': PIPE,
        'r': STDOUT,
    }

    popen_out = None
    popen_err = None
    timeout = None

    def __init__(self, command_line, flags, is_last_command):
        self.args = shlex.split(command_line)
        self.is_last_command = is_last_command
        self.popen_out, self.popen_err, self.timeout = \
            None, None, None
        self.popen_out, self.popen_err, self.timeout = \
            self._process_flags(flags)

    def _process_flags(self, flags):
        out_flag = flags[0]
        err_flag = flags[1]

        if out_flag == 'd':
            if self.is_last_command:
                out_flag = 't'
            else:
                out_flag = 'i'

        if err_flag == 'd':
            err_flag = 't'

        flags = flags[0:2]
        try:
            timeout = int(flags[2:])
        except ValueError:
            timeout = None

        return (self.out_pipes[out_flag], self.err_pipes[err_flag], timeout)

    def __call__(self, input=None):
        p = Popen(self.args,
                  stdin=PIPE,
                  stdout=self.popen_out,
                  stderr=self.popen_err,
                  shell=False,
                  universal_newlines=True,
                  )

        stdout, stderr = p \
            .communicate(input=input, timeout=self.timeout)
        return (stdout, stderr)


class Pipe:
    def __init__(self, *cmds):
        self.cmds = cmds
        self()
        pass

    def __call__(self):
        input = None
        for idx, cmd in enumerate(self.cmds):
            if type(cmd) == tuple:
                command_line = cmd[0]
                flags = cmd[1]
                try:
                    # if flags contain only timeout
                    int(flags)
                    flags = f'dd{flags}'
                except ValueError:
                    pass
            else:
                command_line = cmd
                flags = 'dd'

            is_last_command = (idx == len(self.cmds) - 1)
            c = Command(command_line, flags, is_last_command)
            input, _ = c(input=input)
