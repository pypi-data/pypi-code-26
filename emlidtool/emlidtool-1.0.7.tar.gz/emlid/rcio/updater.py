import progressbar

from emlid.rcio.versionchecker import VersionChecker as FirmwareVersionChecker, CrcNotFoundError
from emlid.util.util import root_should_execute, UpdateError
from termcolor import colored
from subprocess import PIPE, STDOUT, Popen, check_output, CalledProcessError
from queue import Queue, Empty
from threading import Thread


class FirmwareUpdater:
    def __init__(self, firmware_path='/lib/firmware/rcio.fw', verbose_update=False):
        self.alive_path = '/sys/kernel/rcio/status/alive'
        self.verbose_update = verbose_update
        self._firmware_path = firmware_path
        self._bar = progressbar.ProgressBar(redirect_stdout=True)

        self.kill_blackmagic()

        self.commands = {
            'Connect': [b'tar ext:4242\n'],
            'Attach': [b'mon swdp_scan\n', b'attach 1\n'],
            'Catch vectors': [b'monitor vector_catch disable hard\n'],
            'Erase': [b'mon erase_mass\n'],
            'Load': [b'set mem inaccessible-by-default off\n', b'load\n'],
            'Run': [b'set confirm off\n', b'run\n']
        }

        self.action_sequence = [
            ('Connect', b'Remote debugging using :4242'),
            ('Attach', b'Attaching'),
            ('Catch vectors', b'Catching vectors: reset'),
            ('Erase', b'erase\n'),
            ('Load', b'Transfer rate'),
            ('Run', b'Starting program'),
        ]

        self.restart_sequence = [
            ('Connect', b'Remote debugging using :4242'),
            ('Attach', b'Attaching'),
            ('Catch vectors', b'Catching vectors: reset'),
            ('Run', b'Starting program'),
        ]

        # launch blackmagic and arm-none-eabi-gdb
        self.queue = Queue()
        gdb_args = ['stdbuf', '-oL', 'arm-none-eabi-gdb', self._firmware_path]
        self.gdb_client = Popen(gdb_args, bufsize=1, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        blackmagic_args = ['stdbuf', '-oL', 'blackmagic']
        self.bm = Popen(blackmagic_args, stdout=PIPE, stderr=STDOUT)

        # start updater_thread that reads output from gdb_client
        self.updater_thread = Thread(target=self.enqueue_output, args=(self.gdb_client.stdout, self.queue))
        self.updater_thread.daemon = True
        self.updater_thread.start()
        self.update_status = 0

    @root_should_execute
    def update(self, quiet_update, force_update):
        self.quiet_update = quiet_update
        if not force_update:
            if not FirmwareVersionChecker(self._firmware_path).update_needed():
                self.kill_subprocesses()
                print(colored("Nothing to update! You're using the newest firmware.", 'green'))
                return

        if not self.check_blackmagic():
            raise UpdateError('Blackmagic failed to start')

        if not self.quiet_update:
            print('Updating firmware using {}'.format(self._firmware_path))

        for action in self.action_sequence:
            self.perform_action(action[0], action[1])

        if not self.verbose_update:
            if not self.quiet_update:
                self._bar.finish()

        self.kill_subprocesses()
        print(colored("You have successfully updated RCIO firmware", 'green'))
        print(colored("\nYou need to reboot your device\n", "yellow"))

    @root_should_execute
    def restart(self):
        self.quiet_update=True
        for action in self.restart_sequence:
            self.perform_action(action[0], action[1])

        self.kill_subprocesses()
        alive = self.check_alive()
        if alive is 1:
            print(colored('RCIO has restarted successfully', 'green'))
        else:
            print(colored('RCIO has not been restarted', 'red'))

    def check_alive(self):
        try:
            with open(self.alive_path, 'r') as f:
                return int(f.read().strip(), 16)
        except FileNotFoundError:
            raise CrcNotFoundError('Please verify that rcio_spi is loaded and'
                                   ' {crc_path} exists'.format(alive=self.alive_path))

    def kill_subprocesses(self):
        self.gdb_client.kill()
        self.bm.kill()

    def perform_action(self, action, status):
        for command in self.commands[action]:
            self.send_command(command)

        if self.verbose_update:
            self.check_status_verbose(status, action)
        else:
            if not self.quiet_update:
                self._bar.update(self.update_status)
            self.update_status += 10
            if b'load' in command:
                print(colored('Flashing', 'yellow'))
                self.check_status_load(b'Flash Write')
            self.check_status(status, action)
            if not self.quiet_update:
                print(colored('{}: done'.format(action), 'green'))

    def send_command(self, command):
        self.gdb_client.stdin.write(command)
        self.gdb_client.stdin.flush()

    def check_status_verbose(self, expect_str, action):
        print("\n===================================================")
        print(colored('PERFORMING ACTION: {}'.format(action), 'blue'))
        print(colored('CAUGHT OUTPUT:\n', 'blue'))
        self.check_status(expect_str, action)
        print(colored('{}: OK'.format(action), 'green'))
        print("===================================================\n")

    def check_status(self, expect_str, action):
        while True:
            try:
                if action is 'Load':
                    output_line = self.queue.get(0.1)
                else:
                    output_line = self.queue.get(timeout=3)
            except Empty:
                if expect_str in b'erase\n':
                    return
                if action is 'Load':
                    continue
                if not self.verbose_update:
                    if not self.quiet_update:
                        self._bar.finish()
                raise UpdateError('Cannot update RCIO firmware')
            else:
                if self.verbose_update:
                    print(output_line)
                if expect_str in output_line:
                    return

    def check_status_load(self, expect_str):
        loading_started = False
        start = 40
        parts_written = 0
        for line in iter(self.bm.stdout.readline, b''):
            if expect_str in line:
                parts_written += 1
                if not self.quiet_update:
                    self._bar.update(start + parts_written)
                loading_started = True
            if loading_started:
                if b'Unsupported' in line:
                    break

    def check_blackmagic(self):
        for line in iter(self.bm.stdout.readline, b''):
            if b'Listening on TCP:4242' in line:
                return True
        return False

    @staticmethod
    def kill_blackmagic():
        try:
            check_output("killall blackmagic", shell=True, stderr=STDOUT)
        except CalledProcessError:
            return False
        else:
            return True


    @staticmethod
    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    @property
    def firmware(self):
        return self._firmware_crc
