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
Helper classes/functions for the unit tests
"""
import json

from mock import Mock


class MockBugzilla(object):
    def __init__(self, product='Fedora', package='nethack'):
        self.logged_in = False
        self._product = product
        self._package = package

    def login(self, *args, **kwargs):
        self.logged_in = True

    def getbug(self, bug_id):
        if self.logged_in:
            reviewer = 'mjordan@redhat.com'
            creator = 'akhairna@redhat.com'
        else:
            reviewer = 'Michael Jordan'
            creator = 'Apoorv Khairnar'

        mock_rv = Mock()
        mock_rv.creator = creator
        mock_rv.component = 'Package Review'
        mock_rv.product = self._product
        mock_rv.assigned_to = reviewer
        mock_rv.setter = reviewer
        mock_rv.flags = [{'status': '+',
                          'name': 'fedora-review',
                          'type_id': 65,
                          'is_active': 1,
                          'id': bug_id,
                          'setter': reviewer}]
        mock_rv.summary = ('Review Request: {0} - A rogue-like single'
                           'player dungeon exploration game'.format(
                               self._package))
        return mock_rv


def get_mock_sla_rv(name='security_fixes'):
    mock_rv = Mock()
    mock_rv.ok = True
    mock_rv.json.return_value = {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [
            {
                'id': 1,
                'name': name,
                'description': name
            }
        ]
    }
    return mock_rv


def get_mock_new_branch_issue(branch, sla=None, repo='nethack'):
    content = {
        'action': 'new_branch',
        'repo': repo,
        'namespace': 'rpms',
        'branch': branch,
        'create_git_branch': True
    }

    if sla:
        content['sls'] = sla

    title = 'New Branch "{0}" for "rpms/nethack"'.format(branch)
    return title, content


def get_mock_new_issue_invalid_action():
    content = {'action': 'Invalid action'}
    content = '```\n{0}\n```'.format(json.dumps(content, indent=True))
    issue = {
        'id': 1,
        'title': 'Issue title',
        'user': {'fullname': 'Apoorv Khairnar', 'name': 'akhairna'},
        'status': 'Open',
        'content': content}
    return issue


def get_mock_new_repo_issue(branch, sla=None, repo='nethack', exception=False):
    content = {
        'bug_id': '1441813',
        'repo': repo,
        'description': '',
        'branch': branch,
        'action': 'new_repo',
        'upstreamurl': '',
        'summary': 'A rogue-like single player dungeon exploration game',
        'namespace': 'rpms',
        'monitor': 'monitoring-with-scratch'
    }
    if sla:
        content['sls'] = sla
    if exception:
        content['bug_id'] = ''
        content['exception'] = True

    title = 'New Repo for "rpms/nethack"'
    return title, content


def get_mock_issue_rv(branch, sla=None, ticket_type='new_repo',
                      repo='nethack', exception=False):
    mock_rv = Mock()
    mock_rv.ok = True
    if ticket_type == 'new_repo':
        title, content = get_mock_new_repo_issue(branch, sla, repo, exception)
    else:
        title, content = get_mock_new_branch_issue(branch, sla, repo)

    mock_rv.json.return_value = build_issue(2, title, content)
    return mock_rv


def get_mock_new_issue_rv(branch, sla=None, ticket_type='new_repo'):
    mock_rv = Mock()
    mock_rv.ok = True
    if ticket_type == 'new_repo':
        title, content = get_mock_new_repo_issue(branch, sla)
    else:
        title, content = get_mock_new_branch_issue(branch, sla)
    mock_rv.json.return_value = {
        'message': 'Issue created',
        'issue': build_issue(2, title, content)}
    return mock_rv


def build_issue(issue_id, title, content):
    if isinstance(content, dict):
        content = '```\n{0}\n```'.format(json.dumps(content, indent=True))

    issue = {
        'assignee': None,
        'blocks': [],
        'close_status': None,
        'close_at': None,
        'comments': [],
        'content': content,
        'custom_fields': [],
        'date_created': '1499283461',
        'depends': [],
        'id': issue_id,
        'last_updated': '1499283461',
        'milestone': '',
        'priority': None,
        'private': False,
        'status': 'Open',
        'tags': [],
        'title': title,
        'user': {'fullname': 'Apoorv Khairnar', 'name': 'akhairna'}
    }
    return issue


def get_mock_issue_rv_from_issue_dict(issue):
    mock_rv = Mock()
    mock_rv.ok = True
    mock_rv.json.return_value = issue
    return mock_rv


def get_mock_issues_rv(issues):
    mock_rv = Mock()
    mock_rv.ok = True

    args_obj = {
        'assignee': None,
        'author': None,
        'no_stones': None,
        'priority': None,
        'since': None,
        'status': 'Open',
        'milestones': [],
        'tags': []
    }
    mock_rv.json.return_value = {
        'args': args_obj,
        'issues': issues,
        'total_issues': len(issues)
    }
    return mock_rv


def get_mock_pagure_project(exists=False):
    mock_rv = Mock()
    mock_rv.ok = exists
    if exists:
        mock_rv.status_code = 200
        mock_rv.json.return_value = {
            'access_groups': {
                'admin': [],
                'commit': [],
                'ticket': []
            },
            'access_users': {
                'admin': [],
                'commit': [],
                'owner': [
                  'lmacken'
                ],
                'ticket': []
            },
            'close_status': [],
            'custom_keys': [],
            'date_created': '1500070131',
            'description': 'The nethack rpms',
            'fullname': 'rpms/nethack',
            'id': 10309,
            'milestones': {},
            'name': 'nethack',
            'namespace': 'rpms',
            'parent': None,
            'priorities': {},
            'tags': [],
            'user': {
                'fullname': 'lmacken',
                'name': 'lmacken'
            }
        }
    else:
        mock_rv.status_code = 404
        mock_rv.json.return_value = {
            'error': 'Project not found',
            'error_code': 'ENOPROJECT'
        }
    return mock_rv


def get_mock_pagure_git_urls(is_project=False):
    mock_rv = Mock()
    mock_rv.ok = True
    rv = {
        'total_urls': 2,
        'urls': {}
    }

    if is_project:
        rv['urls']['git'] = 'https://distgit.local/rpms/nethack.git'
        rv['urls']['ssh'] = 'ssh://distgit.local/rpms/nethack.git'
    else:
        rv['urls']['git'] = \
            'https://distgit.local/releng/fedora-scm-requests.git'
        rv['urls']['ssh'] = \
            'ssh://distgit.local/releng/fedora-scm-requests.git'
    mock_rv.json.return_value = rv
    return mock_rv


def get_mock_pdc_branch(branch_name, exists=False):
    mock_rv = Mock()
    mock_rv.ok = True
    mock_rv.status_code = 200
    if exists:
        mock_rv.json.return_value = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': 143066,
                    'global_component': 'nethack',
                    'name': branch_name,
                    'slas': [
                        {
                            'id': 284850,
                            'sla': 'security_fixes',
                            'eol': '2018-07-01'
                        },
                        {
                            'id': 284841,
                            'sla': 'bug_fixes',
                            'eol': '2018-07-01'
                        }
                    ],
                    'type': 'rpm',
                    'active': True,
                    'critical_path': False
                }
            ]
        }
    else:
        mock_rv.json.return_value = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }
    return mock_rv


def get_mock_pdc_global_component(exists=True):
    mock_rv = Mock()
    mock_rv.ok = True
    mock_rv.status_code = 200
    if exists:
        mock_rv.json.return_value = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': 30008,
                    'name': 'nethack',
                    'dist_git_path': None,
                    'dist_git_web_url': ('https://pkgs.example.com/cgit/rpms/'
                                         'nethack'),
                    'labels': [],
                    'upstream': None
                }
            ]
        }
    else:
        mock_rv.json.return_value = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }
    return mock_rv


def get_mock_users_query(user):
    mock_rv = Mock()
    mock_rv.ok = True
    mock_rv.status_code = 200
    mock_rv.json.return_value = {
        'mention': [
            {
                'image': ('https://seccdn.libravatar.org/avatar/7af4373297380a'
                          'aa84f377164d26672315dbcb68ef781132e2c3828e234b8e6b'
                          '?s=16&d=retro'),
                'name': user,
                'username': user
            },
            {
                'image': ('https://seccdn.libravatar.org/avatar/7af4373297380a'
                          'aa84f377164d26672315dbcb68ef781132e2c3828e234b8e6b'
                          '?s=16&d=retro'),
                'name': 'Tom Brady',
                'username': 'tbrady'
            }
        ],
        'total_users': 1,
        'users': [
            user,
            'tbrady'
        ]
    }
    return mock_rv


def get_mock_el_check_rv():
    mock_rv = Mock()
    mock_rv.ok = True
    mock_rv.json.return_value = {
        'arches': ['noarch', 'x86_64', 'i686', 'ppc64', 'ppc', 'ppc64le'],
        'packages': {
            'kernel': {'arch': ['noarch', 'x86_64', 'ppc64', 'ppc64le']},
            'glibc': {'arch': ['i686', 'x86_64', 'ppc', 'ppc64', 'ppc64le']}
        }
    }
    return mock_rv
