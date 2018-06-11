# -*- coding: utf-8 -*-
#
# This file is part of fedscm_admin.
# Copyright © 2018 Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
"""
pytest tests for utils
"""

from __future__ import absolute_import
import tempfile
import os
from unittest import TestCase

from click import ClickException
from mock import patch, Mock
from requests import ConnectionError

import tests.mock_values as mock_values


class TestGeneral(TestCase):
    def setUp(self):
        import fedscm_admin.bugzilla
        self.mock_bz_patcher = patch.object(
            fedscm_admin.bugzilla.BugzillaClient, 'client',
            mock_values.MockBugzilla())
        self.mock_bz = self.mock_bz_patcher.start()

    def tearDown(self):
        self.mock_bz_patcher.stop()

    @patch('fedscm_admin.request_utils.retry_session')
    def test_requests_wrapper_error(self, mock_retry_session):
        """
        Verifies that a ClickException is raised if a ConnectionError is
        raised
        """
        from fedscm_admin.request_utils import requests_wrapper
        mock_error_request = Mock()
        mock_error_request.url = 'https://pagure.io'
        mock_session = Mock()
        mock_session.get.side_effect = ConnectionError(
            'error', request=mock_error_request)
        mock_retry_session.return_value = mock_session
        try:
            requests_wrapper(
                'https://pagure.io', service_name='Pagure', timeout=30)
            assert 'ClickException not called'
        except ClickException as error:
            assert str(error) == ('Could not connect to "Pagure" at '
                                  'https://pagure.io. Please try again.')

    def test_get_request_json_error_with_json_and_key(self):
        from fedscm_admin.request_utils import get_request_json
        mock_rv = Mock()
        mock_rv.ok = False
        mock_rv.status_code = 404
        mock_rv.json.return_value = {'error': 'not found'}
        mock_rv.request.url = 'https://pagure.io'
        try:
            get_request_json(mock_rv, 'Testing the app', 'error')
            assert 'ClickException not called'
        except ClickException as error:
            assert str(error) == ('A failure occurred while Testing the app '
                                  'at https://pagure.io. The status code was '
                                  '"404". The error was "not found".')

    def test_get_request_json_error_with_json_no_key(self):
        from fedscm_admin.request_utils import get_request_json
        mock_rv = Mock()
        mock_rv.ok = False
        mock_rv.status_code = 404
        mock_rv.json.return_value = {'error': 'not found'}
        mock_rv.request.url = 'https://pagure.io'
        try:
            get_request_json(mock_rv, 'Testing the app')
            assert 'ClickException not called'
        except ClickException as error:
            assert str(error) == ('A failure occurred while Testing the app '
                                  'at https://pagure.io. The status code was '
                                  '"404". The error was '
                                  '"{\'error\': \'not found\'}".')

    def test_get_request_json_error_no_json(self):
        from fedscm_admin.request_utils import get_request_json
        mock_rv = Mock()
        mock_rv.ok = False
        mock_rv.status_code = 404
        mock_rv.json.side_effect = ValueError('not JSON')
        mock_rv.request.url = 'https://pagure.io'
        try:
            get_request_json(mock_rv, 'Testing the app')
            assert 'ClickException not called'
        except ClickException as error:
            assert str(error) == ('A failure occurred while Testing the app '
                                  'at https://pagure.io. The status code was '
                                  '"404". The error was "".')

    def test_get_request_json_error_500(self):
        from fedscm_admin.request_utils import get_request_json
        mock_rv = Mock()
        mock_rv.ok = False
        mock_rv.status_code = 500
        mock_rv.request.url = 'https://pagure.io'
        try:
            get_request_json(mock_rv, 'Testing the app')
            assert 'ClickException not called'
        except ClickException as error:
            assert str(error) == ('A failure occurred while Testing the app '
                                  'at https://pagure.io. The status code was '
                                  '"500".')

    @patch('fedscm_admin.request_utils.retry_session')
    def test_verify_slas(self, mock_retry_session):
        """
        Verifies the provided SLAs
        """
        from fedscm_admin.utils import verify_slas
        from fedscm_admin import VERSION
        expected_url = ('https://pdc.local/rest_api/v1/component-sla-types/'
                        '?name=security_fixes')
        mock_session = Mock()
        mock_session.get.return_value = mock_values.get_mock_sla_rv()
        mock_retry_session.return_value = mock_session
        for eol in ['2025-12-01', '2025-06-01']:
            assert verify_slas(None, {'security_fixes': eol}) is None
            headers = {'User-Agent': 'fedscm-admin/{0}'.format(VERSION)}
            mock_session.get.assert_called_once_with(
                expected_url, headers=headers, timeout=60)
            mock_session.get.reset_mock()

    @patch('fedscm_admin.request_utils.retry_session')
    def test_verify_slas_eol_expired(self, mock_retry_session):
        """
        Tests that expired SLAs raise an exception.
        """
        from fedscm_admin.utils import verify_slas
        from fedscm_admin.exceptions import ValidationError

        mock_session = Mock()
        mock_session.get.return_value = mock_values.get_mock_sla_rv()
        mock_retry_session.return_value = mock_session

        try:
            slas = {'security_fixes': '2001-12-01', 'bug_fixes': '2030-12-01'}
            verify_slas('abc', slas)
            assert False, 'An exception was not raised'
        except ValidationError as e:
            assert str(e) == 'The SL "2001-12-01" is already expired'

    @patch('fedscm_admin.request_utils.retry_session')
    def test_verify_slas_invalid_date(self, mock_retry_session):
        """
        Tests verify_slas with an SLA that is not June 1st or December 1st. An
        error is expected.
        """
        from fedscm_admin.utils import verify_slas
        from fedscm_admin.exceptions import ValidationError

        mock_session = Mock()
        mock_session.get.return_value = mock_values.get_mock_sla_rv()
        mock_retry_session.return_value = mock_session

        for eol in ['2030-01-01', '2030-12-25']:
            try:
                slas = {'security_fixes': eol, 'bug_fixes': '2030-12-01'}
                verify_slas('abc', slas)
                assert False, 'An exception was not raised'
            except ValidationError as e:
                assert str(e) == ('The SL "{0}" must expire on June 1st or '
                                  'December 1st'.format(eol))

    def test_config_path_in_env_variable(self):
        """
        Tests that a configuration file that is defined in FEDSCM_ADMIN_CONFIG
        can be used.
        """
        import fedscm_admin.config
        tmp_file = tempfile.mktemp()
        with open(tmp_file, 'w') as tmp_file_stream:
            tmp_file_stream.write('[admin]\ntest_config_item = test_value')
        with patch('os.environ.get', side_effect=['true', tmp_file]):
            config = fedscm_admin.config.get_config()
            os.remove(tmp_file)
            rv = fedscm_admin.config.get_config_item(config, 'test_config_item')

        assert rv == 'test_value'
