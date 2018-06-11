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
pytest tests for fedscm-admin
"""
from __future__ import absolute_import
from unittest import TestCase

from click.testing import CliRunner
from mock import patch, Mock

import tests.mock_values as mock_values


def get_latest_fedora_branch(slas):
    for branch in slas.keys():
        if branch.startswith('f'):
            return branch
    raise RuntimeError('No Fedora branch was found in the test')


class FedScmAdmin(TestCase):
    def setUp(self):
        self.mock_fas_patcher = patch('fedora.client.AccountSystem')
        self.mock_fas = self.mock_fas_patcher.start()
        mock_fas_account_system = Mock()
        mock_fas_account_system._AccountSystem__alternate_email = \
            {'email@domain.com': 123204}
        mock_fas_account_system.person_by_id.return_value = {
            'username': 'akhairna',
            'group_roles': {
                'factory2': {
                    'role_status': 'approved',
                    'sponsor_id': 112617,
                    'person_id': 21008,
                    'approval': '2016-09-23 18:48:35.556056+00:00',
                    'group_id': 100301,
                    'role_type': 'user'
                },
                'packager': {
                    'internal_comments': None,
                    'role_status': 'approved',
                    'creation': '2017-06-28 17:10:55.065315+00:00',
                    'sponsor_id': 146058,
                    'person_id': 21008,
                    'approval': '2017-06-28 17:11:02.618607+00:00',
                    'group_id': 100300,
                    'role_type': 'user'
                }
            }
        }
        mock_people_query = Mock()
        mock_people_query.id = 21008
        mock_fas_account_system.people_query.return_value = \
            [mock_people_query]
        mock_fas_account_system.verify_credentials.return_value = True
        self.mock_fas.return_value = mock_fas_account_system

        self.mock_git_patcher = patch('fedscm_admin.git.GitRepo')
        self.mock_git = self.mock_git_patcher.start()
        self.mock_git_obj = Mock()
        self.mock_git_obj.first_commit = \
            '1d4ff81bba43bcfce9582b2caf2bca413bfd3730'
        self.mock_git.return_value = self.mock_git_obj

        import fedscm_admin.bugzilla
        self.mock_bz_patcher = patch.object(
            fedscm_admin.bugzilla.BugzillaClient, 'client',
            mock_values.MockBugzilla())
        self.mock_bz = self.mock_bz_patcher.start()

    def tearDown(self):
        self.mock_bz_patcher.stop()
        self.mock_fas_patcher.stop()
        self.mock_git_obj.reset_mock()
        self.mock_git_patcher.stop()

    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_list(self, mock_retry_session):
        """
        Tests fedscm-admin with the option 'list'
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        issue_title, issue_content = \
            mock_values.get_mock_new_repo_issue('master')
        issue = mock_values.build_issue(1, issue_title, issue_content)
        branch_issue_title, branch_issue_content = \
            mock_values.get_mock_new_branch_issue(
                'abc', {'security_fixes': '2025-12-01'})
        branch_issue = mock_values.build_issue(
            2, branch_issue_title, branch_issue_content)
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issues_rv([branch_issue, issue])
        ]
        mock_retry_session.return_value = mock_session

        runner = CliRunner()
        result = runner.invoke(fedscm_admin_cli, ['list'])
        expected_rv = ('#1: New Repo for "rpms/nethack" (opened by akhairna)\n'
                       '#2: New Branch "abc" for "rpms/nethack" (opened by '
                       'akhairna)\n')
        assert result.exit_code == 0
        assert result.output == expected_rv

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process(self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a non-standard branch
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', sla={'security_fixes': '2025-06-01'}),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pagure_git_urls()
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\n')
        assert result.exit_code == 0
        assert result.output.count('- Adding comment to Pagure issue') == 1
        assert result.output.count('- Adding comment to rhbz#') == 1
        outputs = [
            'New Repo for "rpms/nethack"',
            'The Pagure repository was created',
            'You may commit to the branch "abc" in about 10 minutes.'
        ]
        for output in outputs:
            assert output in result.output
        # One for fedora-scm-requests
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_force(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a non-standard branch
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', sla={'security_fixes': '2025-12-01'}),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pagure_git_urls()
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2', '--force'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\n')
        assert result.exit_code == 0
        assert '- Skipping verification of RHBZ' in result.output
        assert 'WARNING:          The Bugzilla bug validation was skipped' \
            in result.output
        assert result.output.count('- Adding comment to Pagure issue') == 1
        assert result.output.count('- Adding comment to rhbz#') == 1
        outputs = [
            'New Repo for "rpms/nethack"',
            'The Pagure repository was created',
            'You may commit to the branch "abc" in about 10 minutes.'
        ]
        for output in outputs:
            assert output in result.output
        # One for fedora-scm-requests
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_exception(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin on a ticket for a repo with a non-standard
        branch and with the exception flag set to True
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', sla={'security_fixes': '2025-12-01'}, exception=True),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pagure_git_urls()
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\n')
        assert result.exit_code == 0
        assert '- Skipping verification of RHBZ' in result.output
        error = ('WARNING:          The requester states this request is an '
                 'exception and doesn\'t require Bugzilla validation. Please '
                 'manually verify it.')
        assert error in result.output
        assert result.output.count('- Adding comment to Pagure issue') == 1
        outputs = [
            'New Repo for "rpms/nethack"',
            'The Pagure repository was created',
            'You may commit to the branch "abc" in about 10 minutes.'
        ]
        for output in outputs:
            assert output in result.output
        # One for fedora-scm-requests
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_standard_branch_no_sla(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a standard branch and no sla provided
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('master'),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pagure_git_urls()
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\n')
        assert result.exit_code == 0
        assert 'New Repo for "rpms/nethack"' in result.output
        assert 'The Pagure repository was created' in result.output
        assert 'You may create the branch' not in result.output
        # One for fedora-scm-requests
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_epel7(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with an EPEL7 branch and no sla provided
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        import fedscm_admin.bugzilla
        self.mock_bz_patcher.stop()
        self.mock_bz_patcher = patch.object(
            fedscm_admin.bugzilla.BugzillaClient, 'client',
            mock_values.MockBugzilla('Fedora EPEL'))
        self.mock_bz = self.mock_bz_patcher.start()
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('epel7'),
            mock_values.get_mock_el_check_rv(),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_branch('epel7', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_branch('epel7', exists=False),
            mock_values.get_mock_pagure_git_urls()
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\n')
        assert result.exit_code == 0
        assert 'New Repo for "rpms/nethack"' in result.output
        assert 'The Pagure repository was created' in result.output
        assert 'You may commit to the branch "epel7" in about 10 minutes.' in \
            result.output
        # One for fedora-scm-requests
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_master_epel_bz_prduct(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with the master branch and the Bugzilla bug's product is
        "Fedora EPEL"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        import fedscm_admin.bugzilla
        self.mock_bz_patcher.stop()
        self.mock_bz_patcher = patch.object(
            fedscm_admin.bugzilla.BugzillaClient, 'client',
            mock_values.MockBugzilla('Fedora EPEL'))
        self.mock_bz = self.mock_bz_patcher.start()
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('master'),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pagure_git_urls()
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\n')
        assert result.exit_code == 0
        assert 'New Repo for "rpms/nethack"' in result.output
        assert 'The Pagure repository was created' in result.output
        # One for fedora-scm-requests
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_deny(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a standard branch with action "deny"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('master'),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False)
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '1'],
            input='mprahl\n12345\nmprahl\n12345\ndeny\nNA\n')
        assert result.exit_code == 0
        assert 'New Repo for "rpms/nethack"' in result.output
        assert 'Please enter a comment explaining the denial' in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_skip(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a standard branch with action "skip"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('master'),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False)
        ]
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '1'],
            input='mprahl\n12345\nmprahl\n12345\nskip\nn\n')
        assert result.exit_code == 0
        assert 'New Repo for "rpms/nethack"' in result.output
        assert 'The Pagure repository was created' not in result.output
        assert 'You may create the branch' not in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_new_branch_deny(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new branch
        request for a repo with a standard branch with action "deny"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'master', ticket_type='new_branch'),
            mock_values.get_mock_pagure_project(exists=True),
            mock_values.get_mock_pagure_git_urls(is_project=True),
            mock_values.get_mock_pdc_branch('master', exists=False)
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\ndeny\nNA\n')
        assert result.exit_code == 0
        assert 'New Branch "master" for "rpms/nethack"' in result.output
        assert 'Please enter a comment explaining the denial' in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_standard_branch_skip(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new branch
        request for a repo with a standard branch with action "skip"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'master', ticket_type='new_branch'),
            mock_values.get_mock_pagure_project(exists=True),
            mock_values.get_mock_pagure_git_urls(is_project=True),
            mock_values.get_mock_pdc_branch('master', exists=False)
        ]
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '1'],
            input='mprahl\n12345\nmprahl\n12345\nskip\nn\n')
        assert result.exit_code == 0
        assert 'New Branch "master" for "rpms/nethack"' in result.output
        assert 'The Pagure repository was created' not in result.output
        assert 'You may create the branch' not in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas')
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_invalid_sla(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with invalid slas provided
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin.exceptions import ValidationError
        mock_slas.side_effect = ValidationError('Invalid SLAs')
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', {'security_fixes': '2025-12-01'})
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '1'],
            input='mprahl\n12345\nmprahl\n12345\ny\n')
        assert result.exit_code == 0
        assert 'Error:     Invalid SLAs' in result.output
        assert 'Would you like to close the ticket as invalid' in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_epel7_invalid_package(
            self, mock_retry_session, mock_slas):
        """
        Tests that fedscm-admin will not allow a new EPEL package that is
        already an official EL package
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        import fedscm_admin.bugzilla
        from fedscm_admin import INVALID_EPEL_ERROR
        self.mock_bz_patcher.stop()
        self.mock_bz_patcher = patch.object(
            fedscm_admin.bugzilla.BugzillaClient, 'client',
            mock_values.MockBugzilla('Fedora EPEL', 'kernel'))
        self.mock_bz = self.mock_bz_patcher.start()
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('epel7', repo='kernel'),
            mock_values.get_mock_el_check_rv()
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\ny\n')
        assert result.exit_code == 0
        error = ('Error:     {0}'.format(INVALID_EPEL_ERROR))
        assert error in result.output
        assert 'Would you like to close the ticket as invalid' in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_branch_epel7_invalid_package(
            self, mock_retry_session, mock_slas):
        """
        Tests that fedscm-admin will not allow a new EPEL branch of a
        package that is already an official EL package
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin import INVALID_EPEL_ERROR
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'epel7', ticket_type='new_branch', repo='kernel'),
            mock_values.get_mock_pagure_project(exists=True),
            mock_values.get_mock_pagure_git_urls(),
            mock_values.get_mock_el_check_rv()
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\ny\n')
        assert result.exit_code == 0
        error = ('Error:     {0}'.format(INVALID_EPEL_ERROR))
        assert error in result.output
        assert 'Would you like to close the ticket as invalid' in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_invalid_action(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" with invalid action
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        issue = mock_values.get_mock_new_issue_invalid_action()
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv_from_issue_dict(issue)
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '1'],
            input='mprahl\n12345\nmprahl\n12345\ny\nn\n')
        assert result.exit_code == 0
        assert 'Error:     Invalid ticket body' in result.output
        assert 'Would you like to close the ticket as invalid' in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_pagure_already_exists(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo that already exists in Pagure
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from tests import mock_values
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('master'),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(True)]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mmprahl\n12345\nprahl\n12345\ny\nn\n')
        assert 'The Pagure project already exists' in result.output
        assert 'Would you like to close the ticket as invalid?' in \
            result.output
        assert result.exit_code == 0
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_pdc_already_exists(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a branch already in PDC
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from tests import mock_values
        mock_session = Mock()
        mock_post = Mock()
        mock_post.ok = True
        mock_post.json.return_value = {}
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv('master'),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=True)
        ]
        mock_session.post.return_value = mock_post
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\ny\nn\n')
        assert 'Error:     The PDC branch already exists' in result.output
        assert 'Would you like to close the ticket as invalid' in result.output
        assert result.exit_code == 0
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_processall(self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "processall" on a new repo
        request and a new branch request
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin import STANDARD_BRANCH_SLAS
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        issue_title, issue_content = mock_values.get_mock_new_repo_issue(
            'master', STANDARD_BRANCH_SLAS['master'])
        issue = mock_values.build_issue(1, issue_title, issue_content)
        branch_issue_title, branch_issue_content = \
            mock_values.get_mock_new_branch_issue(
                'abc', {'security_fixes': '2025-12-01'})
        branch_issue = mock_values.build_issue(
            2, branch_issue_title, branch_issue_content)
        mock_session.get.side_effect = [
            mock_values.get_mock_issues_rv([branch_issue, issue]),
            mock_values.get_mock_users_query('akhairna'),
            mock_values.get_mock_pagure_project(exists=False),
            mock_values.get_mock_pdc_branch('master', exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch(None, exists=False),
            mock_values.get_mock_pagure_git_urls(),
            mock_values.get_mock_pagure_project(exists=True),
            mock_values.get_mock_pagure_git_urls(is_project=True),
            mock_values.get_mock_pdc_branch(None, exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pagure_git_urls(is_project=True),
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['processall'],
            input='mprahl\n12345\nmprahl\n12345\napprove\nn\napprove\nn\n')
        assert result.exit_code == 0
        assert 'New Branch "abc" for "rpms/nethack"' in result.output
        assert 'New Repo for "rpms/nethack"' in result.output
        assert 'All done!' in result.output
        # One for fedora-scm-requests and one for getting the inital commit
        assert self.mock_git_obj.clone_repo.call_count == 2
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_new_branch_auto_approve(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new branch
        request with "--auto-approve".
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin import STANDARD_BRANCH_SLAS
        mock_session = Mock()
        mock_rv = Mock()
        mock_rv.ok = True
        mock_rv.json.return_value = {}
        branch_name = None
        for branch in STANDARD_BRANCH_SLAS.keys():
            if branch.startswith('f'):
                branch_name = branch
        if not branch_name:
            raise ValueError('No standard branch name could be found that is '
                             'auto-approvable')

        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                branch_name, ticket_type='new_branch'),
            mock_values.get_mock_pagure_project(exists=True),
            mock_values.get_mock_pagure_git_urls(is_project=True),
            mock_values.get_mock_pdc_branch(None, exists=False),
            mock_values.get_mock_pdc_global_component(exists=True),
            mock_values.get_mock_pdc_branch('abc', exists=False),
            mock_values.get_mock_pagure_git_urls(is_project=True),
        ]
        mock_session.post.return_value = mock_rv
        mock_session.patch.return_value = mock_rv
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2', '--auto-approve'],
            input='mprahl\n12345\nmprahl\n12345\n')
        assert result.exit_code == 0
        expected = ('Auto-approving the new branch request for "{0}" on '
                    'rpms/nethack'.format(branch_name))
        assert expected in result.output
        assert 'Closing Pagure issue 2' in result.output
        # One for getting the inital commit
        assert self.mock_git_obj.clone_repo.call_count == 1
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.pagure.get_request_json')
    @patch('fedscm_admin.pagure.requests_wrapper')
    def test_get_git_url_no_username(self, requests, json):
        import fedscm_admin.pagure
        target = 'a git url, amazing.'
        json.return_value = {'urls': {'ssh': target}}
        url = fedscm_admin.pagure.get_scm_requests_git_url()
        self.assertEqual(url, target)

    @patch('fedscm_admin.pagure.get_request_json')
    @patch('fedscm_admin.pagure.requests_wrapper')
    def test_get_git_url_with_username(self, requests, json):
        import fedscm_admin.pagure
        response = 'ssh://src.fp.o/amazing'
        target = 'ssh://joe@src.fp.o/amazing'
        json.return_value = {'urls': {'ssh': response}}
        url = fedscm_admin.pagure.get_scm_requests_git_url(username='joe')
        self.assertEqual(url, target)

    @patch('fedscm_admin.request_utils.retry_session')
    def test_fas_bad_password(self, mock_retry_session):
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin import FAS_CLIENT
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', sla={'security_fixes': '2025-12-01'})]
        mock_retry_session.return_value = mock_session

        with patch.object(FAS_CLIENT.client, 'verify_password') as mock_verify:
            mock_verify.return_value = False
            runner = CliRunner()
            result = runner.invoke(
                fedscm_admin_cli, ['process', '2'],
                input='mprahl\n12345\n')
            assert ('Error: The login to FAS failed. Please make sure you '
                    'typed in the correct credentials.') in result.output
            assert result.exit_code == 1

    @patch('fedscm_admin.request_utils.retry_session')
    def test_bugzilla_bad_password(self, mock_retry_session):
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin.bugzilla import BugzillaError
        from fedscm_admin import BUGZILLA_CLIENT
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', sla={'security_fixes': '2025-12-01'})]
        mock_retry_session.return_value = mock_session

        with patch.object(BUGZILLA_CLIENT.client, 'login') as mock_verify:
            mock_verify.side_effect = BugzillaError('Invalid credentials')
            runner = CliRunner()
            result = runner.invoke(
                fedscm_admin_cli, ['process', '2'],
                input='mprahl\n12345\nmprahl\n12345\n')
            assert ('Error: The login to Bugzilla failed. Please make sure '
                    'you typed in the correct credentials.') in result.output
            assert result.exit_code == 1

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_epel_wrong_bz_product(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with an epel branch but the Bugzilla bug is for the product
        "Fedora" and not "Fedora EPEL"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_session.get.side_effect = [mock_values.get_mock_issue_rv('epel7')]
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\nn\n')
        assert result.exit_code == 0
        error = ('Error:     The Bugzilla bug is for "Fedora" but the '
                 'requested branch is an EPEL branch')
        assert error in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_master_wrong_bz_product(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a master branch but the Bugzilla bug is for the product
        "Fedora EPEL" and not "Fedora"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        import fedscm_admin.bugzilla
        from fedscm_admin import STANDARD_BRANCH_SLAS
        self.mock_bz_patcher.stop()
        self.mock_bz_patcher = patch.object(
            fedscm_admin.bugzilla.BugzillaClient, 'client',
            mock_values.MockBugzilla('Fedora EPEL'))
        self.mock_bz = self.mock_bz_patcher.start()
        chosen_branch = get_latest_fedora_branch(STANDARD_BRANCH_SLAS)
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(chosen_branch)]
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\nn\n')
        assert result.exit_code == 0
        error = ('Error:     The Bugzilla bug is for "Fedora EPEL" but the '
                 'requested branch is "{0}"'.format(chosen_branch))
        assert error in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_master_wrong_bz_creator(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo requested by "imposter" but the bug creator is "akhairna"
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        from fedscm_admin import STANDARD_BRANCH_SLAS

        chosen_branch = get_latest_fedora_branch(STANDARD_BRANCH_SLAS)
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(chosen_branch)]
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        mock_path = 'fedscm_admin.BugzillaClient.get_fas_user_by_bz_email'
        with patch(mock_path, return_value={'username': 'imposter'}):
            result = runner.invoke(
                fedscm_admin_cli, ['process', '2'],
                input='mprahl\n12345\nmprahl\n12345\nn\n')
        assert result.exit_code == 0
        error = ('Error:     The Bugzilla review bug creator didn\'t match '
                 'the requester in Pagure.')
        assert error in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0

    @patch('fedscm_admin.utils.verify_slas', return_value=None)
    @patch('fedscm_admin.request_utils.retry_session')
    def test_fedscm_admin_process_bad_name(
            self, mock_retry_session, mock_slas):
        """
        Tests fedscm-admin with the option "process" on a new repo request
        for a repo with a bad branch name
        """
        from fedscm_admin.fedscm_admin import cli as fedscm_admin_cli
        mock_session = Mock()
        mock_session.get.side_effect = [
            mock_values.get_mock_issue_rv(
                'abc', sla={'security_fixes': '2025-12-01'}, repo='nethack*3')]
        mock_retry_session.return_value = mock_session
        runner = CliRunner()
        result = runner.invoke(
            fedscm_admin_cli, ['process', '2'],
            input='mprahl\n12345\nmprahl\n12345\nN\n')
        assert result.exit_code == 0
        error = ('Error:     The repository name is invalid. It must be at '
                 'least two characters long with only letters, numbers, '
                 'hyphens, underscores, plus signs, and/or periods. Please '
                 'note that the project cannot start with a period or a plus '
                 'sign.')
        assert error in result.output
        assert self.mock_git_obj.clone_repo.call_count == 0
        assert self.mock_git_obj.set_monitoring_on_repo.call_count == 0
