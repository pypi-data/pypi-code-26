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
Pagure API helper functions
"""
from __future__ import absolute_import
from six.moves.urllib.parse import urlencode

import click

from fedscm_admin import CONFIG
from fedscm_admin.config import get_config_item
from fedscm_admin.request_utils import (
    get_auth_header, requests_wrapper, get_request_json)


def get_pagure_auth_header(token_type='ticket'):
    """
    Get a dictionary of the headers needed to make an authenticated API
    call to Pagure
    :param token_type: a string of the type of token used (e.g. ticket or
    global)
    :return: a dictionary of the headers needed to make an authenticated API
    call to Pagure
    """
    prefix = 'pagure'
    if token_type == 'ticket':
        prefix = 'pagure_ticket'
    return get_auth_header(prefix)


def get_project(namespace, repo):
    """
    Get an existing Pagure project
    :param namespace: a string representing the namespace to create the project
    in
    :param repo: a string of the project/repo name
    :return: a dictionary representing the project or None
    """
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
    pagure_project_url = \
        '{0}/api/0/{1}/{2}'.format(pagure_url.rstrip('/'), namespace, repo)

    rv = requests_wrapper(
        pagure_project_url, timeout=60, service_name='Pagure')
    if rv.status_code == 404:
        return None
    else:
        return get_request_json(rv, 'getting a project in Pagure')


def user_exists(username):
    """  Return True if a given pagure user exists
    :param username: a string of the user's username
    :return: True or False
    """
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
    pagure_project_url = \
        '{0}/api/0/users?pattern={1}'.format(pagure_url.rstrip('/'), username)

    rv = requests_wrapper(
        pagure_project_url, timeout=60, service_name='Pagure')
    data = get_request_json(rv, 'getting a user in Pagure')
    return username in data['users']


def get_issue(issue_id):
    """
    Get an issue from the ticket queue
    :return: a dictionary representing the issue or None
    """
    pagure_url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    pagure_api_url = '{0}/api/0'.format(pagure_url)
    pagure_repo_issue_url = '{0}/releng/fedora-scm-requests/issue/{1}'.format(
        pagure_api_url, issue_id)

    issue_rv = requests_wrapper(
        pagure_repo_issue_url, timeout=60, service_name='Pagure')
    if issue_rv.status_code == 404:
        return None
    return get_request_json(issue_rv, 'getting an issue', 'error')


def get_issues():
    """
    List all the issues in ticket queue
    :return: a list of dictionaries containing issues
    """
    pagure_url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    pagure_api_url = '{0}/api/0'.format(pagure_url)
    pagure_repo_issues_url = \
        '{0}/releng/fedora-scm-requests/issues?{1}'.format(
            pagure_api_url, urlencode({'status': 'Open'}))

    issues_rv = requests_wrapper(
        pagure_repo_issues_url, timeout=60, service_name='Pagure')
    return get_request_json(
        issues_rv, 'getting open issues', 'error')['issues']


def get_pagure_issue_url(issue_id):
    """
    Get the URL to the issue in the UI
    :param issue_id: a string of the issue ID
    :return: a string of the URL to the issue in the UI
    """
    url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    return '{0}/releng/fedora-scm-requests/issue/{1}'.format(url, issue_id)


def get_project_git_url(namespace, repo, url_type='ssh', username=None):
    """
    Get the Git URL of a project
    :param namespace: a string representing the namespace to create the project
    in
    :param repo: a string of the project/repo name
    :param url_type: a string of the type of Git URL (e.g. ssh, git, etc.)
    :param username: a string of the username that is cloning the repo. This
    can be None as well.
    :return: a string of the Git URL
    """
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url').rstrip('/')
    pagure_git_url_api_url = '{0}/api/0/{1}/{2}/git/urls'.format(
        pagure_url, namespace, repo)
    rv = requests_wrapper(
        pagure_git_url_api_url, timeout=60, service_name='Pagure')
    rv_json = get_request_json(rv, 'getting a project\'s git url', 'error')
    url = rv_json['urls'].get(url_type)

    # Insert the username *if* relevant.
    if username is not None and url.startswith('ssh://') and '@' not in url:
        url = 'ssh://{username}@{rest}'.format(
            username=username, rest=url[6:])
    return url


def get_scm_requests_git_url(url_type='ssh', username=None):
    """
    Get the Git URL of a project
    :param namespace: a string representing the namespace to create the project
    in
    :param repo: a string of the project/repo name
    :param url_type: a string of the type of Git URL (e.g. ssh, git, etc.)
    :param username: a string of the username that is cloning the repo. This
    can be None as well.
    :return: a string of the Git URL
    """
    pagure_url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    pagure_git_url_api_url = pagure_url + \
        '/api/0/releng/fedora-scm-requests/git/urls'

    rv = requests_wrapper(
        pagure_git_url_api_url, timeout=60, service_name='Pagure')
    rv_json = get_request_json(rv, 'getting the scm-requests url.', 'error')
    url = rv_json['urls'].get(url_type)

    # Insert the username *if* relevant.
    if username is not None and url.startswith('ssh://') and '@' not in url:
        url = 'ssh://{username}@{rest}'.format(
            username=username, rest=url[6:])
    return url


def new_project(namespace, repo, description, upstreamurl):
    """
    Create a new Pagure project
    :param namespace: a string representing the namespace to create the project
    in
    :param repo: a string of the project/repo name
    :param description: a string of the description of the project
    :param upstreamurl: a string of the URL of the upstream project
    :return: None
    """
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
    pagure_new_project_url = \
        '{0}/api/0/new'.format(pagure_url.rstrip('/'))

    headers = get_pagure_auth_header('global')
    payload = {
        'namespace': namespace,
        'name': repo,
        'description': description or 'The {0} package'.format(repo),
        'url': upstreamurl or '',
        'create_readme': True,
        'wait': True
    }

    click.echo('- Creating new pagure project {0}/{1}'.format(namespace, repo))
    rv = requests_wrapper(
        pagure_new_project_url, data=payload, headers=headers, timeout=90,
        http_verb='post', service_name='Pagure')
    # We won't actually use the returned output from this function call but
    # it does error checking for us
    get_request_json(rv, 'creating a new project in Pagure')
    return None


def add_comment_to_issue(issue_id, comment):
    url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    issue_api_url = '{0}/api/0/releng/fedora-scm-requests/issue/{1}'.format(
        url, issue_id)
    issue_comment_api_url = '{0}/comment'.format(issue_api_url)
    headers = get_pagure_auth_header()
    comment_payload = {'comment': comment}
    click.echo('- Adding comment to Pagure issue {0}'.format(issue_id))
    rv = requests_wrapper(
        issue_comment_api_url, data=comment_payload, headers=headers,
        timeout=60, http_verb='post', service_name='Pagure')
    # We won't use the JSON but it gives us good error checking
    get_request_json(rv, 'adding a comment to an issue', 'error')


def close_issue(issue_id, comment=None, close_status=None):
    """
    Close a Pagure issue
    :param issue_id: the id of the ticket to close
    :param comment: the comment to leave in the issue before closing
    :param close_status: the close status of the issue. These have to be
    configured in the project.
    :return: None
    """
    url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    issue_api_url = '{0}/api/0/releng/fedora-scm-requests/issue/{1}'.format(
        url, issue_id)
    issue_status_api_url = '{0}/status'.format(issue_api_url)
    headers = get_pagure_auth_header()

    if comment is not None:
        add_comment_to_issue(issue_id, comment)

    status_payload = {'status': 'Closed'}
    if close_status is not None:
        status_payload['close_status'] = close_status
    click.echo('- Closing Pagure issue {0}'.format(issue_id))
    rv = requests_wrapper(
        issue_status_api_url, data=status_payload, headers=headers,
        timeout=60, http_verb='post', service_name='Pagure')
    # We won't use the JSON but it gives us good error checking
    get_request_json(rv, 'changing the status of an issue', 'error')


def change_project_main_admin(namespace, repo, new_main_admin):
    """
    Change the main admin/owner of a project
    :param namespace: a string representing the namespace to create the project
    in
    :param repo: a string of the project/repo name
    :param new_main_admin: a string of the username of the new main admin
    :return: None
    """
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
    pagure_modify_project_url = \
        '{0}/api/0/{1}/{2}'.format(pagure_url.rstrip('/'), namespace, repo)

    headers = get_pagure_auth_header('global')
    payload = {
        'main_admin': new_main_admin
    }
    click.echo('- Changing Pagure main admin for {0}/{1} to {2}.'.format(
        namespace, repo, new_main_admin))
    rv = requests_wrapper(
        pagure_modify_project_url, data=payload, headers=headers,
        timeout=60, http_verb='patch', service_name='Pagure')
    get_request_json(rv, 'setting the owner of a project in Pagure')
    return None


def generate_acls_on_project(namespace, repo, wait=False):
    """
    Tell Pagure to generate the Gitolite ACLs on a project
    :param namespace: a string representing the namespace of the project
    :param repo: a string of the project/repo name
    :return: None
    """
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
    pagure_git_acl_url = '{0}/api/0/{1}/{2}/git/generateacls'.format(
        pagure_url.rstrip('/'), namespace, repo)
    headers = get_pagure_auth_header('global')
    payload = {'wait': wait}
    click.echo('- Generating the Gitolite ACLs on {0}/{1}'.format(
        namespace, repo))
    rv = requests_wrapper(
        pagure_git_acl_url, data=payload, headers=headers,
        timeout=300, http_verb='post', service_name='Pagure')
    get_request_json(rv, 'generating the Gitolite ACLs of a project in Pagure')
    return None


def new_branch(namespace, repo, branch, from_commit=None, from_branch=None):
    """
    Create a new git branch in Pagure
    :param namespace: a string representing the namespace of the project
    :param repo: a string of the project/repo name
    :param branch: a string of the git branch to create
    :param from_commit: a string of the commit to branch off of in the new git
    branch. This is required if `from_branch` is not set.
    :param from_branch: a string of the branch to branch off of in the new git
    branch. This is required if `from_commit` is not set.
    :return: None
    """
    if from_commit and from_branch:
        raise RuntimeError('`from_commit` and `from_branch` were both '
                           'specified. Only use one.')
    elif not from_commit and not from_branch:
        raise RuntimeError('You must specify either `from_commit` or '
                           '`from_branch`')

    url = get_config_item(CONFIG, 'pagure_dist_git_url')
    branch_url = '{0}/api/0/{1}/{2}/git/branch'.format(
        url.rstrip('/'), namespace, repo)
    headers = get_pagure_auth_header('global')
    payload = {'branch': branch}
    if from_commit:
        payload['from_commit'] = from_commit
    else:
        payload['from_branch'] = from_branch
    click.echo('- Creating the git branch "{0}" on {1}/{2} from "{3}"'.format(
        branch, namespace, repo, from_commit or from_branch))
    rv = requests_wrapper(
        branch_url, data=payload, headers=headers, timeout=60,
        http_verb='post', service_name='Pagure')
    get_request_json(rv, 'create a git branch on a project in Pagure')
    return None
