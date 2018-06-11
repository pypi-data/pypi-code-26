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
Provides helper functions
"""
from __future__ import absolute_import

import re
import json
from datetime import datetime

import click
from six import string_types
from six.moves import xmlrpc_client

from fedscm_admin.config import get_config_item
from fedscm_admin import (
    CONFIG, MONITOR_CHOICES, BUGZILLA_CLIENT, FAS_CLIENT, STANDARD_BRANCH_SLAS,
    INVALID_EPEL_ERROR, is_epel)
import fedscm_admin.pdc
import fedscm_admin.pagure
import fedscm_admin.git
from fedscm_admin.request_utils import requests_wrapper, get_request_json
from fedscm_admin.exceptions import ValidationError


def login_to_bugzilla_with_user_input():
    """
    A helper function to prompt for the username and password to Bugzilla and
    login to Bugzilla
    :return: None
    """
    logged_in = False
    # An exception is thrown when the session cache is expired. Systems without
    # the session cached at all, will return False.
    try:
        logged_in = BUGZILLA_CLIENT.client.logged_in
    except xmlrpc_client.Error:
        pass

    if logged_in is False:
        username = click.prompt('Please enter your Bugzilla username')
        password = click.prompt(
            'Please enter your Bugzilla password', hide_input=True)
        BUGZILLA_CLIENT.login(username, password)
        # Force the password out of RAM
        del password


def login_to_fas_with_user_input():
    """
    A helper function to prompt for the username and password to FAS and store
    those in the FAS object (yuck)
    :return: None
    """
    username = click.prompt('Please enter your FAS username')
    password = click.prompt('Please enter your FAS password', hide_input=True)
    FAS_CLIENT.set_credentials(username, password)
    # Force the password out of RAM
    del password


def verify_slas(branch, sla_dict):
    """
    Verifies that SLAs are properly formatted and exist in PDC
    :param branch: a string of the branch name to verify or None
    :param sla_dict: a dictionary with the SLAs of the request
    :return: None or ValidationError
    """
    if not isinstance(sla_dict, dict):
        raise ValueError('The object provided is not a dict')

    if branch is not None and is_valid_standard_branch(branch):
        standard_branch_sla_dict = get_standard_branch_sla_dict(branch)
        if standard_branch_sla_dict == sla_dict:
            return
        else:
            raise ValidationError('The SLs for the branch "{0}" are '
                                  'incorrect'.format(branch))

    eol_date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')
    for sla, eol in sla_dict.items():
        if not isinstance(eol, string_types):
            raise ValidationError(
                'The SL\'s EOL is not a string. It was type "{0}".'
                .format(type(eol).__name__))
        if re.match(eol_date_regex, eol):
            eol_date = datetime.strptime(eol, '%Y-%m-%d').date()
            today = datetime.utcnow().date()
            if eol_date < today:
                raise ValidationError(
                    'The SL "{0}" is already expired'.format(eol))
            elif eol_date.month not in [6, 12] or eol_date.day != 1:
                raise ValidationError(
                    'The SL "{0}" must expire on June 1st or December 1st'
                    .format(eol))
        else:
            raise ValidationError(
                'The EOL date "{0}" is in an invalid format'.format(eol))

        sla_obj = fedscm_admin.pdc.get_sla(sla)
        if not sla_obj:
            raise ValidationError('The SL "{0}" is not in PDC'.format(sla))


def sla_dict_to_list(sla_dict):
    """
    Converts an SLA dictionary to a list {'security_fixes': '2020-01-01'} =>
    ['security_fixes:2020-01-01']
    :param sla_dict: a dictionary with the SLAs of the request
    :return: a list of the SLAs
    """
    sla_list = []
    for sla, eol in sla_dict.items():
        sla_list.append('{0}:{1}'.format(sla, eol))

    return sla_list


def is_valid_standard_branch(branch):
    """
    Checks if the branch is a standard branch that hasn't gone EOL
    :param branch: a string of the branch
    :return: boolean
    """
    return branch in STANDARD_BRANCH_SLAS.keys()


def get_standard_branch_sla_dict(branch):
    """
    Gets the SLAs of a standard branch
    :param branch: a string of the branch
    :return: a dictionary of the SLAs for that standard branch or a
    ValidationError
    """
    if is_valid_standard_branch(branch):
        return STANDARD_BRANCH_SLAS[branch]

    raise ValidationError('"{0}" is not a valid or supported standard branch'
                          .format(branch))


def prompt_for_ticket_action():
    """
    A helper function to continuously prompt the user for an action
    :return: a string representing the action the user has chosen
    """
    while True:
        choices = ['approve', 'deny', 'skip']
        prompt_msg = ('\nHow would you like to handle the ticket? ({0})'
                      .format('/'.join(choices)))
        action = click.prompt(prompt_msg, default='skip')
        action = action.lower()
        if action == 'a':
            action = 'approve'
        elif action == 'd':
            action = 'deny'
        elif action == 's':
            action = 'skip'
        if action in choices:
            return action
        else:
            click.echo('An invalid answer was provided. Please try again.')


def list_all_tickets():
    """
    List all the tickets in the queue in short form
    :return: None
    """
    # Sort the issues so that the oldest get shown first
    issues = fedscm_admin.pagure.get_issues()[::-1]
    for issue in issues:
        issue_id = issue['id']
        issue_title = issue['title'].strip()
        issue_owner = issue['user']['name']
        click.echo('#{0}: {1} (opened by {2})'.format(
            issue_id, issue_title, issue_owner))


def process_all_tickets(auto_approve=False):
    """
    Process all the tickets in the queue one by one
    :param auto_approve: a boolean that determines if new branch requests that
    don't require approval can be automatically approved and processed. This
    defaults to False.
    :return: None
    """
    # Sort the issues so that the oldest get processed first
    issues = fedscm_admin.pagure.get_issues()[::-1]
    for issue in issues:
        process_ticket(issue, auto_approve=auto_approve)

    if len(issues) > 0:
        click.echo('\nAll done!')
    else:
        click.echo('There are no issues in the queue')


def process_ticket(issue, force=False, auto_approve=False):
    """
    Process a single ticket
    :param issue: a dictionary of the issue's JSON
    :param force: a boolean to skip Bugzilla bug validation
    :param auto_approve: a boolean that determines if new branch requests that
    don't require approval can be automatically approved and processed. This
    defaults to False.
    :return: None
    """
    try:
        # If a ValueError is raised, that means it isn't valid JSON
        issue_body = json.loads(issue['content'].strip('`').strip('\n'))
    except ValueError:
        prompt_to_close_bad_ticket(issue)
        return

    if 'sls' in issue_body:
        try:
            # If a ValueError is raised, that means they aren't valid SLAs
            click.echo('- Verifying service-levels from the ticket.')
            verify_slas(issue_body.get('branch', None), issue_body['sls'])
        except ValidationError as error:
            prompt_to_close_bad_ticket(issue, str(error))
            return
    else:
        branch = issue_body.get('branch', '').strip()
        if issue_body.get('action') in ['new_repo', 'new_branch'] and branch:
            try:
                # If the SLAs aren't defined and the branch is a standard
                # branch, an SLA will be assigned. Otherwise, a ValidationError
                # will be raised and nothing will get assigned. Future code
                # will prompt the admin to close this ticket as bad for missing
                # the SLA.
                issue_body['sls'] = get_standard_branch_sla_dict(branch)
            except ValidationError:  # pragma: no cover
                pass

    if 'branch' in issue_body and 'namespace' in issue_body \
            and issue_body['namespace'] in ['modules', 'test-modules'] \
            and not valid_module_stream_name(issue_body['branch']):
        error_msg = ('Only characters, numbers, periods, dashes, underscores, '
                     'and pluses are allowed in module branch names')
        prompt_to_close_bad_ticket(issue_body, error_msg)
        return

    if 'monitor' in issue_body \
            and issue_body['monitor'].strip() not in MONITOR_CHOICES:
        error_msg = ('The monitor choice of "{0}" is invalid'
                     .format(issue_body['monitor']))
        prompt_to_close_bad_ticket(issue, error_msg)

    if issue_body.get('action') == 'new_repo':
        prompt_for_new_repo(issue, issue_body, force=force,
                            auto_approve=auto_approve)
    elif issue_body.get('action') == 'new_branch':
        prompt_for_new_branch(issue, issue_body, auto_approve=auto_approve)
    else:
        prompt_to_close_bad_ticket(issue)
        return


def prompt_for_new_repo(issue_json, issue_body_json, force=False,
                        auto_approve=False):
    """
    A helper function that prompts the user with information on a new repo
    ticket
    :param issue_json: the dictionary representing the JSON of the issue
    returned from Pagure
    :param issue_body_json: a partially validated dictionary of the JSON in the
    issue body
    :param force: a boolean to skip Bugzilla bug validation
    :param auto_approve: a boolean that determines if requests that don't
    require approval can be automatically approved and processed. This
    defaults to False. This currently does nothing.
    :return: None
    """
    required_keys = [
        'repo', 'branch', 'bug_id', 'action', 'namespace', 'sls',
        'monitor']
    for key in required_keys:
        if key not in issue_body_json.keys():
            prompt_to_close_bad_ticket(issue_json)
            return

    requester = issue_json['user']['name']
    namespace = issue_body_json['namespace'].strip()
    repo = issue_body_json['repo'].strip()
    bug_id = str(issue_body_json['bug_id']).strip()
    branch_name = issue_body_json['branch'].strip()
    exception = issue_body_json.get('exception', False)

    if not valid_project_name(repo):
        error = ('The repository name is invalid. It must be at least two '
                 'characters long with only letters, numbers, hyphens, '
                 'underscores, plus signs, and/or periods. Please note that '
                 'the project cannot start with a period or a plus sign.')
        prompt_to_close_bad_ticket(issue_json, error)
        return

    if force or exception is True or namespace == 'modules':
        skip_msg = '- Skipping verification of RHBZ'
        if bug_id:
            skip_msg = '{0} #{1}'.format(skip_msg, bug_id)
        click.echo(skip_msg)
    else:
        if not bug_id:
            prompt_to_close_bad_ticket(
                issue_json, 'An invalid Bugzilla bug was provided')
        try:
            click.echo('- Checking that #{0} is a valid RHBZ.'.format(bug_id))
            BUGZILLA_CLIENT.get_valid_review_bug(
                bug_id, repo, branch_name, require_auth=True,
                check_fas=True, namespace=namespace, pagure_user=requester)
        except ValidationError as error:  # pragma: no cover
            prompt_to_close_bad_ticket(issue_json, str(error))
            return

    # If the provided SLA is in an invalid format, a ValueError will raise
    try:
        sla_list = sla_dict_to_list(issue_body_json['sls'])
    except ValueError:
        prompt_to_close_bad_ticket(issue_json)
        return

    # This should never trigger because if the user requested an EPEL branch
    # here, it'd have to be accompanied by a Bugzilla bug for the "Fedora EPEL"
    # product. So this will only trigger if the reviewer made a mistake.
    if is_epel(branch_name) and not valid_epel_package(repo, branch_name):
        prompt_to_close_bad_ticket(issue_json, INVALID_EPEL_ERROR)
        return

    issue_id = issue_json['id']
    issue_owner = issue_json['user']['name']
    click.echo('- Checking if user {0} has an account in dist-git.'.format(
        issue_owner))
    pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
    if not fedscm_admin.pagure.user_exists(issue_owner):
        sync_comment = ('@{0} needs to login to {1} to sync accounts '
                        'before we can proceed.'.format(
                            issue_owner, pagure_url))
        question = '{0}  Post this comment to the ticket?'.format(
            sync_comment)
        if click.confirm(question):
            fedscm_admin.pagure.add_comment_to_issue(issue_id, sync_comment)
        return

    click.echo('- Checking if {0}/{1} already exists in dist-git.'.format(
        namespace, repo))
    project = fedscm_admin.pagure.get_project(namespace, repo)
    if project:
        prompt_to_close_bad_ticket(
            issue_json, 'The Pagure project already exists')
        return

    description = issue_body_json['description'].strip()
    upstreamurl = issue_body_json['upstreamurl'].strip()
    component_type = fedscm_admin.pdc.component_type_to_singular(namespace)
    master_branch = None
    if branch_name != 'master':
        click.echo('- Checking if master already exists in PDC.')
        master_branch = fedscm_admin.pdc.get_branch(
            repo, 'master', component_type)

    click.echo('- Checking if {0} already exists in PDC.'.format(branch_name))
    branch = fedscm_admin.pdc.get_branch(repo, branch_name, component_type)

    if master_branch or branch:
        prompt_to_close_bad_ticket(
            issue_json, 'The PDC branch already exists')
        return

    issue_title = issue_json['title'].strip()
    issue_ui_url = fedscm_admin.pagure.get_pagure_issue_url(issue_id)
    bz_bug_url = ''
    if bug_id:
        bz_bug_url = BUGZILLA_CLIENT.get_bug_url(bug_id)

    click.echo('\nTicket #{0}'.format(issue_id))
    click.echo('    Ticket Title:     {0}'.format(issue_title))
    click.echo('    Ticket Opened By: {0}'.format(issue_owner))
    click.echo('    Ticket URL:       {0}'.format(issue_ui_url))
    click.echo('    Bugzilla URL:     {0}'.format(bz_bug_url))
    click.echo('    Action:           New Repo')
    click.echo('    Namespace:        {0}'.format(namespace))
    click.echo('    Name:             {0}'.format(repo))
    click.echo('    Branch:           {0}'.format(branch_name))
    click.echo('    Upstream Url:     {0}'.format(upstreamurl))
    click.echo('    Summary:          {0}'.format(issue_body_json['summary']))
    click.echo('    Description:      {0}'.format(description))
    click.echo('    SLs:              {0}'.format(', '.join(sla_list)))
    click.echo('    Monitor:          {0}'.format(issue_body_json['monitor']))

    if force:
        msg = '    WARNING:          The Bugzilla bug validation was skipped'
        click.secho(msg, fg='yellow')
    elif exception is True:
        msg = ('    WARNING:          The requester states this request is an '
               'exception and doesn\'t require Bugzilla validation. Please '
               'manually verify it.')
        click.secho(msg, fg='yellow')

    action = prompt_for_ticket_action()

    if action == 'approve':
        # Create the PDC SLA entry
        dist_git_url = '{0}/{1}/{2}'.format(
            pagure_url.rstrip('/'), namespace, repo)
        # If the global component already exists, this will not create another
        fedscm_admin.pdc.new_global_component(repo, dist_git_url)
        # Pagure uses plural names for namespaces, but PDC does not use the
        # plural version for branch types
        branch_type = fedscm_admin.pdc.component_type_to_singular(namespace)
        # If the branch requested isn't master, still create a master branch
        # in PDC anyways.
        if branch_name != 'master':
            fedscm_admin.pdc.new_branch(repo, 'master', branch_type)
            for sla, eol in fedscm_admin.STANDARD_BRANCH_SLAS['master'].items():
                fedscm_admin.pdc.new_sla_to_branch(
                    sla, eol, repo, 'master', branch_type)

        fedscm_admin.pdc.new_branch(repo, branch_name, branch_type)
        for sla, eol in issue_body_json['sls'].items():
            fedscm_admin.pdc.new_sla_to_branch(
                sla, eol, repo, branch_name, branch_type)

        # Create the Pagure repo
        fedscm_admin.pagure.new_project(
            namespace, repo, description, upstreamurl)
        # If the branch requested isn't master, create that branch in git. The
        # master branch is already created at this point.
        if branch_name != 'master':
            new_git_branch(namespace, repo, branch_name, use_master=True)
        scm_req_git_url = fedscm_admin.pagure.get_scm_requests_git_url(
            username=FAS_CLIENT.client.username)
        scm_req_git_obj = fedscm_admin.git.GitRepo(scm_req_git_url)
        scm_req_git_obj.clone_repo()
        scm_req_git_obj.set_monitoring_on_repo(
            namespace, repo, issue_body_json['monitor'].strip())
        fedscm_admin.pagure.change_project_main_admin(
            namespace, repo, issue_owner)

        if branch_name == 'master':
            new_repo_comment = ('The Pagure repository was created at {0}'
                                .format(dist_git_url))
        else:
            new_repo_comment = ('The Pagure repository was created at {0}. '
                                'You may commit to the branch "{1}" in about '
                                '10 minutes.'.format(dist_git_url,
                                                     branch_name))
        comment_and_close_ticket(issue_id, bug_id, new_repo_comment)
    elif action == 'deny':
        comment_body = click.prompt(
            'Please enter a comment explaining the denial')
        fedscm_admin.pagure.close_issue(issue_id, comment_body, 'Denied')
        if bug_id:
            BUGZILLA_CLIENT.comment(bug_id, comment_body)
    else:
        # This means the admin is skipping this ticket for now
        return


def prompt_for_new_branch(issue_json, issue_body_json, auto_approve=False):
    """
    A helper function that prompts the user with information on a new branch
    ticket
    :param issue_json: the dictionary representing the JSON of the issue
    returned from Pagure
    :param issue_body_json: a partially validated dictionary of the JSON in the
    issue body
    :param auto_approve: a boolean that determines if new branch requests that
    don't require approval can be automatically approved and processed. This
    defaults to False.
    :return: None
    """
    required_keys = ['action', 'namespace', 'branch', 'sls', 'repo']
    for key in required_keys:
        if key not in issue_body_json.keys():
            prompt_to_close_bad_ticket(issue_json)
            return

    # If the provided SLA is in an invalid format, a ValueError will raise
    try:
        sla_list = sla_dict_to_list(issue_body_json['sls'])
    except ValueError:
        prompt_to_close_bad_ticket(issue_json)
        return

    namespace = issue_body_json['namespace'].strip()
    repo = issue_body_json['repo'].strip()
    bug_id = str(issue_body_json.get('bug_id', '')).strip()
    create_git_branch = issue_body_json.get('create_git_branch', True)

    project = fedscm_admin.pagure.get_project(namespace, repo)
    if not project:
        prompt_to_close_bad_ticket(
            issue_json, 'The Pagure repo does not exist')
        return

    if create_git_branch:
        assert_git_repo_initialized_remotely(namespace, repo)

    branch_name = issue_body_json['branch'].strip()
    if is_epel(branch_name) and not valid_epel_package(repo, branch_name):
        prompt_to_close_bad_ticket(issue_json, INVALID_EPEL_ERROR)
        return
    # Pagure uses plural names for namespaces, but PDC does not use the
    # plural version for branch types
    branch_type = fedscm_admin.pdc.component_type_to_singular(namespace)
    click.echo('- Checking if {0} already exists in PDC.'.format(branch_name))
    pdc_branch = fedscm_admin.pdc.get_branch(repo, branch_name, branch_type)
    if pdc_branch:
        prompt_to_close_bad_ticket(
            issue_json, 'The branch in PDC already exists')
        return

    issue_id = issue_json['id']
    issue_title = issue_json['title'].strip()
    issue_owner = issue_json['user']['name']
    issue_ui_url = fedscm_admin.pagure.get_pagure_issue_url(issue_id)

    auto_approved = False
    if auto_approve and \
            not ticket_requires_approval('new_branch', issue_body_json):
        click.echo('- Auto-approving the new branch request for "{0}" on '
                   '{1}/{2}'.format(branch_name, namespace, repo))
        auto_approved = True
        action = 'approve'
    else:
        click.echo('\nTicket #{0}'.format(issue_id))
        click.echo('    Ticket Title:     {0}'.format(issue_title))
        click.echo('    Ticket Opened By: {0}'.format(issue_owner))
        click.echo('    Ticket URL:       {0}'.format(issue_ui_url))
        click.echo('    Action:           New Branch')
        click.echo('    Namespace:        {0}'.format(namespace))
        click.echo('    Name:             {0}'.format(repo))
        click.echo('    Branch:           {0}'.format(branch_name))
        click.echo('    SLs:              {0}'.format(', '.join(sla_list)))
        click.echo('    Git Branch:       {0}'.format(bool_to_word(
            create_git_branch)))

        action = prompt_for_ticket_action()

    if action == 'approve':
        pagure_url = get_config_item(CONFIG, 'pagure_dist_git_url')
        dist_git_url = '{0}/{1}/{2}'.format(
            pagure_url.rstrip('/'), namespace, repo)
        # If the global component already exists, this will not try to create
        # it
        fedscm_admin.pdc.new_global_component(repo, dist_git_url)
        # Pagure uses plural names for namespaces, but PDC does not use the
        # plural version for branch types
        branch_type = fedscm_admin.pdc.component_type_to_singular(namespace)

        fedscm_admin.pdc.new_branch(repo, branch_name, branch_type)
        for sla, eol in issue_body_json['sls'].items():
            fedscm_admin.pdc.new_sla_to_branch(
                sla, eol, repo, branch_name, branch_type)
        fedscm_admin.pagure.generate_acls_on_project(namespace, repo)

        if create_git_branch:
            new_git_branch(namespace, repo, branch_name)
            new_branch_comment = ('The branch was created in PDC and git. It '
                                  'may take up to 10 minutes before you have '
                                  'write access on the branch.')
        else:
            new_branch_comment = (
                'The branch in PDC was created. Pagure is still processing '
                'the request, but in about 10 minutes, you may create the '
                'branch in Pagure using git.')
        comment_and_close_ticket(issue_id, bug_id, new_branch_comment,
                                 prompt_for_comment=not auto_approved)
    elif action == 'deny':
        comment_body = click.prompt(
            'Please enter a comment explaining the denial')
        fedscm_admin.pagure.close_issue(issue_id, comment_body, 'Denied')
        if bug_id:
            BUGZILLA_CLIENT.comment(bug_id, comment_body)
    else:
        # This means the admin is skipping this ticket for now
        return


def comment_and_close_ticket(issue_id, bug_id, comment=None,
                             close_status='Processed',
                             prompt_for_comment=True):
    """
    A helper function that adds a comment, and then prompts the user if they'd
    like to add one
    :param issue_id: a string or int of the id of the issue to comment and
    close
    :param bug_id: a string or int of the id of the Bugzilla review bug.
    None is an acceptable value if there isn't a bug.
    :param comment: a string of the comment to add to the issue
    :param close_status: a string of the status of the ticket when closed
    :param prompt_for_comment: a boolean that determines the admin should be
    prompted for an extra comment. This defaults to True.
    :return: None
    """
    if comment is not None:
        fedscm_admin.pagure.add_comment_to_issue(issue_id, comment)
        if bug_id:
            BUGZILLA_CLIENT.comment(bug_id, comment)
        click.echo('The following comment was added to the issue "{0}"'
                   .format(comment))
    custom_comment = None
    if prompt_for_comment:
        if click.confirm('Would you like to add another comment?'):
            custom_comment = click.prompt('Please enter a comment')

    fedscm_admin.pagure.close_issue(issue_id, custom_comment, close_status)
    if custom_comment and bug_id:
        BUGZILLA_CLIENT.comment(bug_id, custom_comment)


def prompt_to_close_bad_ticket(issue_json, error='Invalid ticket body'):
    """
    A helper function to automatically prompt the admin if they'd like to close
    the ticket because there is an issue with the request.
    :param issue_json: the dictionary representing the JSON of the issue
    returned from Pagure
    :param error: a string representing the error message that'll be commented
    on the ticket before closing it
    :return: None
    """
    issue_id = issue_json['id']
    issue_title = issue_json['title'].strip()
    issue_owner = issue_json['user']['name']
    url = get_config_item(CONFIG, 'pagure_url').rstrip('/')
    issue_ui_url = '{0}/releng/fedora-scm-requests/issue/{1}'.format(
        url, issue_id)
    bug_id = str(issue_json.get('bug_id', '')).strip()

    click.echo('\nTicket #{0}'.format(issue_id))
    click.echo('    Title:     {0}'.format(issue_title))
    click.echo('    Opened By: {0}'.format(issue_owner))
    click.echo('    URL:       {0}'.format(issue_ui_url))
    click.echo('    Error:     {0}'.format(error))

    if click.confirm('Would you like to close the ticket as invalid?'):
        comment_body = error
        if click.confirm('Would you like to replace the default comment of '
                         '"{0}"?'.format(error)):
            comment_body = click.prompt('Please enter a comment')
        fedscm_admin.pagure.close_issue(issue_id, comment_body, 'Invalid')
        if bug_id:
            BUGZILLA_CLIENT.comment(bug_id, comment_body)


def valid_project_name(project):
    """
    A helper function to determine if a project name meets naming standards
    :param project: a string of the project name
    :return: a boolean detremining if the project name is valid
    """
    return bool(re.match(r'^[a-zA-Z0-9_][a-zA-Z0-9-_.+]*$', project))


def valid_module_stream_name(stream):
    """
    A helper function to determine if a module's stream name meets naming
    standards
    :param stream: a string of the module stream name
    :return: a boolean detremining if the module stream name is valid
    """
    return bool(re.match(r'^[a-zA-Z0-9.\-_+]+$', stream))


def valid_epel_package(name, branch):
    """
    Determines if the package is allowed to have an EPEL branch.
    :param name: a string of the package name
    :param branch: a string of the EPEL branch name (e.g. epel7)
    :return: a boolean
    """
    # Extract any digits in the branch name to determine the EL version
    version = ''.join([i for i in branch if re.match(r'\d', i)])
    url = ('https://infrastructure.fedoraproject.org/repo/json/pkg_el{0}.json'
           .format(version))
    rv = requests_wrapper(
        url, timeout=60, service_name='infrastructure.fedoraproject.org')
    rv_json = get_request_json(rv, 'getting the list of official EL packages')
    # Remove noarch from this because noarch is treated specially
    all_arches = set(rv_json['arches']) - set(['noarch'])
    # On EL6, also remove ppc and i386 as many packages will
    # have these arches missing and cause false positives
    if int(version) == 6:
        all_arches = all_arches - set(['ppc', 'i386'])
    # On EL7 and later, also remove ppc and i686 as many packages will
    # have these arches missing and cause false positives
    elif int(version) >= 7:
        all_arches = all_arches - set(['ppc', 'i686'])
    for pkg_name, pkg_info in rv_json['packages'].items():
        # If the EL package is noarch only or is available on all supported
        # arches, then don't allow an EPEL branch
        if pkg_name == name:
            pkg_arches = set(pkg_info['arch'])
            if pkg_arches == set(['noarch']) or not (all_arches - pkg_arches):
                return False
    return True


def bool_to_word(bool_value):
    """
    Converts a boolean to a "Yes" or "No"
    :param bool_value: a boolean
    :return: a string of the word representing the boolean
    """
    if bool_value is True:
        return 'Yes'
    else:
        return 'No'


def assert_git_repo_initialized_remotely(namespace, repo):
    """
    Determines if the git repo is initialized remotely or not. If it isn't,
    a ValidationError is raised.
    :param namespace: a string of the namespace of the project
    :param project: a string of the project name
    :return: None or ValidationError
    """
    click.echo('- Verifying that the git repo is initialized')
    git_url = fedscm_admin.pagure.get_project_git_url(
        namespace, repo, url_type='git',
        username=FAS_CLIENT.client.username)
    git_obj = fedscm_admin.git.GitRepo(git_url)
    if not git_obj.initialized_remotely:
        raise ValidationError('The git repository is not initialized. The git '
                              'branch can\'t be created.')


def new_git_branch(namespace, repo, branch, use_master=False):
    """
    Create a new branch in git using Pagure. This does some sanity checking
    before sending off the API request.
    :param namespace: a string of the namespace of the project
    :param project: a string of the project name
    :param branch: a string of the branch to create
    :param use_master: a boolean that determines whether to use the master
    branch or the first commit of the master branch as the starting point for
    the new branch
    :return: None or ValidationError
    """
    if use_master is True:
        fedscm_admin.pagure.new_branch(
            namespace, repo, branch, from_branch='master')
    else:
        # Use the git url and not ssh since we only need read-only access. The
        # new branch will be created using the Pagure API and not git directly.
        git_url = fedscm_admin.pagure.get_project_git_url(
            namespace, repo, url_type='git',
            username=FAS_CLIENT.client.username)
        git_obj = fedscm_admin.git.GitRepo(git_url)
        git_obj.clone_repo()
        if not git_obj.initialized:
            raise ValidationError('The git repository is not initialized. A '
                                  'git branch can\'t be created.')
        fedscm_admin.pagure.new_branch(
            namespace, repo, branch, from_commit=git_obj.first_commit)


def ticket_requires_approval(issue_type, issue):
    """
    Determines if the issue requires approval from an administrator.
    :param issue_type: a string determining the issue type
    :param issue: a dictionary of the issue
    :return: a boolean
    """
    # Only some new_branch requests can be auto-approved
    if issue_type != 'new_branch':
        return True

    namespace = issue['namespace'].strip()
    # Only some RPM requests can be auto-approved for now
    if namespace != 'rpms':
        return True

    branch_name = issue['branch'].strip()
    standard_branch = is_valid_standard_branch(branch_name)
    return not(standard_branch and not re.match(r'^(el|epel)[0-9]+$',
               branch_name))
