# pylint: disable=W,C,R
from atexit import register
from os import kill, listdir, remove
from os.path import join
from signal import SIGKILL
from subprocess import PIPE, Popen
from time import sleep

from py_rofi_bus.components.mixins import HasConfig


class ManagesProcesses(HasConfig):
    managed_processes = None

    def __init__(self, *args, **kwargs):
        super(ManagesProcesses, self).__init__(*args, **kwargs)
        if self.managed_processes is None:
            self.managed_processes = {}
        register(self.wipe_processes)
        register(self.demolish_pid_files)

    def check_for_new_scripts(self):
        new_scripts = []
        for file_name in listdir(self.config['load_from']):
            full_file_path = join(self.config['load_from'], file_name)
            result, _ = Popen(
                [
                    'file',
                    '--dereference',
                    full_file_path,
                ],
                stdout=PIPE,
            ).communicate()
            if result.strip().endswith('ASCII text executable'):
                new_scripts.append(full_file_path)
            else:
                print(result)
        return new_scripts

    def load_new_scripts(self, new_scripts):
        for script in new_scripts:
            if script not in self.managed_processes:
                self.managed_processes[script] = Popen(
                    [
                        'bash',
                        '-c',
                        script,
                    ],
                )

    def wipe_processes(self):
        for _, process in list(self.managed_processes.items()):
            try:
                kill(process.pid, SIGKILL)
            except OSError:
                pass

    def demolish_pid_files(self):
        for pid_name in listdir(self.config['pid_folder']):
            full_pid_path = join(self.config['pid_folder'], pid_name)
            with open(full_pid_path, 'r') as pid_file:
                try:
                    kill(int(pid_file.read()), SIGKILL)
                except OSError:
                    pass
            remove(full_pid_path)
