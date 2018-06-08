from __future__ import unicode_literals

import os
import unittest
import warnings

from contextlib import contextmanager
from datetime import date
from unittest.mock import patch, Mock, PropertyMock

from tecplot.exception import *
import tecplot as tp

from test import skip_if_sdk_version_before


@contextmanager
def patch_env(key, val=None):
    saved_val = os.environ.get(key, None)
    try:
        try:
            del os.environ[key]
        except KeyError:
            pass
        if val is not None:
            os.environ[key] = val
        yield
    finally:
        if saved_val is None:
            try:
                del os.environ['HOME']
            except KeyError:
                pass
        else:
            os.environ[key] = saved_val


class TestSession(unittest.TestCase):

    def test_tecplot_directories(self):
        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.tecsdkhome',
                   PropertyMock(return_value='/path/to/tec360')):
            self.assertTrue(tp.session.tecplot_install_directory().startswith('/path'))
            self.assertTrue(tp.session.tecplot_examples_directory().startswith(
                                tp.session.tecplot_install_directory()))

        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.tecsdkhome',
                   PropertyMock(return_value=None)):
            self.assertIsNone(tp.session.tecplot_install_directory())
            self.assertIsNone(tp.session.tecplot_examples_directory())

    def test_stop(self):
        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.stop',
                   Mock(return_value=True)):
            self.assertIsNone(tp.session.stop())

    def test_acquire_license(self):
        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.acquire_license',
                   Mock(return_value=True)):
            self.assertIsNone(tp.acquire_license())

    def test_release_license(self):
        with patch(
                'tecplot.tecutil.tecutil_connector.TecUtilConnector.release_license',
                Mock(return_value=True)):
            self.assertIsNone(tp.release_license())

    @skip_if_sdk_version_before(2017, 3)
    def test_roaming(self):
        if tp.session.connected():
            with self.assertRaises(TecplotLogicError):
                tp.session.start_roaming(10)
        else:
            warnings.simplefilter('ignore')
            tp.session.start_roaming(10)
            self.assertEqual((tp.session.license_expiration() - date.today()).days, 10)
            tp.session.stop_roaming()

    def test_connect(self):
        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.connected',
                   PropertyMock(return_value=False)):
            self.assertFalse(tp.session.connected())

        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.connected',
                   PropertyMock(return_value=True)):
            with patch('tecplot.tecutil.tecutil_client.TecUtilClient.is_server_listening',
                   Mock(return_value=True)):
                self.assertTrue(tp.session.connected())
            with patch('tecplot.tecutil.tecutil_client.TecUtilClient.is_server_listening',
                   Mock(return_value=False)):
                self.assertFalse(tp.session.connected())

        if not tp.session.connected():
            with self.assertRaises(TecplotTimeoutError):
                tp.session.connect(port=1, timeout=0.1, quiet=True)

        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.disconnect',
                   Mock(return_value=None)):
            self.assertIsNone(tp.session.disconnect())

    def test_suspend(self):
        tp.new_layout()
        with tp.session.suspend():
            with tp.session.suspend():
                ds = tp.active_frame().create_dataset('D', ['x', 'y'])
                zn = ds.add_ordered_zone('Z', (1,))
        self.assertEqual(zn.values(0).shape, (1,))


if __name__ == '__main__':
    from .. import main
    main()
