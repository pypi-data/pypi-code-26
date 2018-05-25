import os

from tempfile import NamedTemporaryFile

from termcolor import colored
from emlid.rcio.firmware.firmware import Firmware
from subprocess import check_output, CalledProcessError, STDOUT


class CrcNotFoundError(Exception):
    pass


class InappropriateFirmwareError(Exception):
    pass


class VersionChecker:
    crc_path = '/sys/kernel/rcio/status/crc'
    _objcopy = 'objcopy'

    def __init__(self, firmware_path='/lib/firmware/rcio.fw'):
        self._firmware_path = firmware_path
        self._firmware_max_size = 0xf000

        try:
            with open(self.crc_path, 'r') as f:
                self._crc = int(f.read().strip(), 16)
        except FileNotFoundError:
            raise CrcNotFoundError('Please verify that rcio_spi is loaded and'
                                   ' {crc_path} exists'.format(crc_path=self.crc_path))

    def calculate_crc(self):
        self.make_tmp()
        firmware = Firmware(self._binary_path)
        crc = firmware.crc(self._firmware_max_size)
        os.unlink(self._tmp_binary.name)
        return crc

    def make_tmp(self):
        self._tmp_binary = NamedTemporaryFile(delete=False)
        self._binary_path = self._tmp_binary.name
        self.copy_to_binary()

    def copy_to_binary(self):
        command = ' '.join([self._objcopy, '-O binary', self._firmware_path, self._binary_path])
        try:
            check_output(command, shell=True, stderr=STDOUT)
            return
        except CalledProcessError:
            raise InappropriateFirmwareError('There is an error while updating firmware.\n'
                                             'Please make sure that you have chosen an appropriate one and try again')

    def update_needed(self):
        self._firmware_crc = self.calculate_crc()
        return self._crc != self._firmware_crc

    def check(self, long_output):
        if long_output:
            print('long output')
        if self.update_needed():
            print('current: {}'.format(hex(self._crc)))
            print('local: {}\n'.format(hex(self._firmware_crc)))
            print(colored('You need to update. Please run:', 'yellow'))
            print('emlidtool rcio update')
            return True
        else:
            print(colored('Nothing to update! You are using the newest firmware.', 'green'))
            return False

    @property
    def crc(self):
        return self._crc

