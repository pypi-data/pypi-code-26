import emlid.emlidtool
from .deviceinfostub import *
import emlid.rcio.versionchecker
import emlid.rcio.updater
import emlid.rcio.blackmagic
import emlid.rcio.gdb
import emlid.rcio.firmware.firmware


@pytest.fixture
def versionchecker_nocrc():
    emlid.rcio.versionchecker.VersionChecker.crc_path = 'test_files/rcio/status/nocrc'
    emlid.rcio.versionchecker.VersionChecker._objcopy = 'arm-none-eabi-objcopy'
    return emlid.rcio.versionchecker.VersionChecker


@pytest.fixture
def versionchecker():
    emlid.rcio.versionchecker.VersionChecker.crc_path = 'test_files/rcio/status/crc'
    return emlid.rcio.versionchecker.VersionChecker


@pytest.fixture
def burn():
    emlid.rcio.updater.FirmwareUpdater._burn = 'test_files/rcio/burn/burn.gdb'
    emlid.rcio.updater.FirmwareUpdater._objcopy = 'arm-none-eabi-objcopy'
    return emlid.rcio.updater.FirmwareUpdater


def existing_firmware():
    firmware = emlid.rcio.firmware.firmware.Firmware('test_files/rcio/firmware/test_1.bin')
    return firmware


def test_rcio_versionchecker_nocrc(versionchecker_nocrc):
    with pytest.raises(emlid.rcio.versionchecker.CrcNotFoundError):
        checker = versionchecker_nocrc('test_files/rcio/firmware/rcio-v1-test')


def test_rcio_versionchecker_crc(versionchecker):
    checker = versionchecker('test_files/rcio/firmware/rcio-v1-test')
    assert checker.crc == 0xdeadbeef


def test_rcio_firmware_crc():
    firmware = existing_firmware()
    crc = firmware.crc(padlen=0xf000)
    assert crc == 0x19775137


def test_rcio_no_firmware():
    with pytest.raises(FileNotFoundError):
        firmware = emlid.rcio.firmware.firmware.Firmware('test_files/rcio/firmware/nosuch.bin')


def test_rcio_update_needed(versionchecker):
    checker = versionchecker('test_files/rcio/firmware/rcio-v1-test')
    assert checker.update_needed() is True


def test_rcio_blackmagic_gdb_server_start(capsys):
    expected_output = """Listening on TCP:4242
Resetting TAP
Change state to Shift-IR
Scanning out IRs
jtag_scan: Sanity check failed: IR[0] shifted out as 0
platform_init executuon. jtag_scan returns -1Entring GDB protocol main loop
"""
    gdb_server = emlid.rcio.blackmagic.Blackmagic()
    gdb_server.start()
    out, err = capsys.readouterr()
    assert out == expected_output


def test_rcio_gdb_start(capsys):
    expected_output = """GNU gdb (GDB) 7.6.2
Copyright (C) 2013 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "--host=armv6l-unknown-linux-gnueabihf --target=arm-none-eabi".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>.
(gdb)
"""
    gdb = emlid.rcio.gdb.GDBClient()
    gdb.start()
    out, err = capsys.readouterr()
    assert out == expected_output
