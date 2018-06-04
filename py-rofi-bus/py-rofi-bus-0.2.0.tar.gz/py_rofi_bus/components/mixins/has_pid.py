# pylint:disable=W,C,R

from atexit import register
from os import getpid, kill, remove
from os.path import exists, join

from py_rofi_bus.components.mixins import HasConfig


class HasPid(HasConfig):

    def __init__(self, pid_name='', *args, **kwargs):
        if pid_name:
            kwargs['pid_name'] = pid_name
        HasConfig.__init__(self, *args, **kwargs)
        self.set_pid_name()
        self.clear_pid_file()

    def set_pid_name(self, pid_name=''):
        if 'pid_name' in self.config and self.config['pid_name']:
            self.pid_name = self.config['pid_name']
        elif pid_name:
            self.pid_name = pid_name
        else:
            self.pid_name = ''

    def get_pid_file_name(self):
        return join(
            self.config.config_dir,
            (
                self.config['pid_folder'] if self.pid_name
                else ''
            ),
            "{}.pid".format(self.pid_name),
        )

    def clear_pid_file(self):
        pid_file_name = self.get_pid_file_name()
        if exists(pid_file_name):
            with open(pid_file_name, 'r') as pid_file:
                pid = pid_file.read().strip()
            if pid:
                try:
                    kill(int(pid), 9)
                except OSError:
                    pass
            remove(pid_file_name)

    def write_pid_file(self):
        register(self.remove_pid)
        with open(self.get_pid_file_name(), 'w') as pid_file:
            pid_file.write(str(getpid()))

    def remove_pid(self):
        remove(self.get_pid_file_name())
