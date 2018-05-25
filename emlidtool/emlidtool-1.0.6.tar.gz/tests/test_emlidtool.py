import re
import emlid.emlidtool

from emlid.util.util import NotRootException, FailingTestException
from .deviceinfostub import *
from .devicestub import StubDevice
from mock import patch


def test_version(capsys):
    emlid.emlidtool.show_version()
    out, err = capsys.readouterr()
    assert out == 'Tool not installed systemwide!\n'


def valid_stub_device_information():
    return device_information()()


def no_hat_stub_device_information():
    return no_hat_device_information()()


def valid_stub_device(info):
    return StubDevice()


def test_info(capsys):
    test_args = [sys.argv[0], 'info']
    with patch.object(sys, 'argv', test_args):
        emlid.emlidtool.get_device_information = valid_stub_device_information
        parser = emlid.emlidtool.Emlidtool()
        parser.parse_args()
        out, err = capsys.readouterr()
        assert out == 'Vendor: Emlid Limited\nProduct: Stub\nIssue: Emlid 2017-03-23\nKernel: emlid-kernel-v7\n'


def test_do_tests(caplog):
    emlid.emlidtool.get_device_information = valid_stub_device_information
    emlid.emlidtool.get_device = valid_stub_device
    test_args = [sys.argv[0]]
    with patch.object(sys, 'argv', test_args):
        parser = emlid.emlidtool.Emlidtool()
        try:
            parser.parse_args()
            for record in caplog.records:
                if record.levelname == 'INFO':
                    validation = re.compile('.*PassingTest: Passed')
                    assert validation.match(record.message)
        except FailingTestException:
            pass


def test_rcio_update_quiet():
    test_args = [sys.argv[0], 'rcio', 'update', '-q', '-p', 'test_files/rcio/firmware/test_1.bin']
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            parser = emlid.emlidtool.Emlidtool()
            parser.parse_args()


def test_rcio_update_yes():
    test_args = [sys.argv[0], 'rcio', 'update', '-y', '-p', 'test_files/rcio/firmware/test_1.bin']
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit):
            parser = emlid.emlidtool.Emlidtool()
            parser.parse_args()
