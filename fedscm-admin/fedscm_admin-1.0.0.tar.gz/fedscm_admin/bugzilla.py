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
Provides helper functions for Bugzilla
"""
from __future__ import absolute_import
from six.moves.urllib.parse import urlencode
from datetime import datetime

import click
from click import ClickException
from bugzilla import Bugzilla
# In version 2, BugzillaError was moved to bugzilla.transport
try:
    from bugzilla.transport import BugzillaError
except ImportError:
    from bugzilla import BugzillaError

from fedscm_admin.exceptions import ValidationError
from fedscm_admin import FAS_CLIENT, is_epel


class BugzillaClient(object):
    """
    A helper class to maintain a Bugzilla session
    """
    def __init__(self):
        self.url = 'https://bugzilla.redhat.com'
        self.api_url = '{0}/xmlrpc.cgi'.format(self.url)
        self._client = None
        self.pagure_namespace_to_component = {
            'rpms': 'Package Review',
            'container': 'Container Review',
            'modules': 'Module Review',
            'test-modules': 'Module Review'
        }
        self.pagure_namespace_to_product = {
            'rpms': ['Fedora', 'Fedora EPEL'],
            'container': ['Fedora Container Images'],
            'modules': ['Fedora Modules'],
            'test-modules': ['Fedora']
        }

    @property
    def client(self):
        """
        Returns the initialized client
        """
        if self._client is None:
            try:
                self._client = Bugzilla(self.api_url, use_creds=True)
            except TypeError:
                self._client = Bugzilla(self.api_url)
        return self._client

    def login(self, username, password):
        """
        A login function to Bugzilla. If the password is incorrect, a
        ClickException is raised.
        :param username: a string of the username
        :param password: a string of the password
        :return: None
        """
        try:
            self.client.login(username, password)
        except BugzillaError:
            raise ClickException(
                'The login to Bugzilla failed. Please make sure you typed in '
                'the correct credentials.')

    @staticmethod
    def get_fas_user_by_bz_email(email):
        """
        Searches for a user in FAS by their email address
        :param email: a string of the email address to search with
        :return: a FAS user or None
        """
        if email.endswith('@fedoraproject.org'):
            username = email.split('@fedoraproject.org')[0]
            return FAS_CLIENT.get_fas_user(username)
        else:
            return FAS_CLIENT.get_fas_user(email, search_key='email')

    def get_valid_review_bug(self, bug_id, pkg, branch, require_auth=False,
                             check_fas=False, namespace='rpms',
                             pagure_user=None):
        """
        Checks the validity of a Bugzilla bug representing a Fedora package
        review. This function was inspired by:
        https://github.com/fedora-infra/pkgdb2/blob/master/pkgdb2/api/extras.py
        https://pagure.io/pkgdb-cli/blob/master/f/pkgdb2client/utils.py
        :param bug_id: string or integer of the Bugzilla bug ID
        :param pkg: string of the package name
        :param branch: string of the branch name
        :kwarg require_auth: a boolean determining if an exception is thrown
        if the client is not authenticated
        :kwarg check_fas: a boolean determining if the approver is a packager
        :kwarg namespace: a string of the requested repo's namespace
        :kwarg pagure_user: a string of the requesting user's Pagure username
        :return: Bugzilla bug object
        """
        # When authenticated, you get a user's email address instead of their
        # full name
        if require_auth and not self.client.logged_in:
            raise ValidationError('The Bugzilla client is not authenticated')

        try:
            bug = self.client.getbug(bug_id)
        except Exception as error:
            raise ValidationError(
                'The Bugzilla bug could not be verified. The following '
                'error was encountered: {0}'.format(str(error)))
        # Check that the bug is valid
        bz_proper_component = self.pagure_namespace_to_component.get(namespace)
        bz_proper_products = self.pagure_namespace_to_product.get(namespace)
        if namespace == 'rpms' and branch != 'master':
            if is_epel(branch) and bug.product != 'Fedora EPEL':
                raise ValidationError(
                    'The Bugzilla bug is for "{0}" but the '
                    'requested branch is an EPEL branch'.format(bug.product))
            elif not is_epel(branch) and bug.product == 'Fedora EPEL':
                raise ValidationError(
                    'The Bugzilla bug is for "Fedora EPEL" but the '
                    'requested branch is "{0}"'.format(branch))
        if bz_proper_component is None or bug.component != bz_proper_component:
            raise ValidationError(
                'The Bugzilla bug provided is not the proper type')
        elif bug.product not in bz_proper_products:
            raise ValidationError(
                'The Bugzilla bug provided is not for "{0}"'
                .format('" or "'.join(bz_proper_products)))
        elif bug.assigned_to in ['', None, 'nobody@fedoraproject.org']:
            raise ValidationError(
                'The Bugzilla bug provided is not assigned to anyone')
        if check_fas and require_auth and pagure_user:
            fas_user = self.get_fas_user_by_bz_email(bug.creator)
            if not fas_user:
                raise ValidationError(
                    'The Bugzilla review bug creator could not be found in '
                    'FAS. Make sure your FAS email address is the same as in '
                    'Bugzilla.')
            if fas_user['username'] != pagure_user:
                raise ValidationError('The Bugzilla review bug creator '
                                      'didn\'t match the requester in Pagure.')
        # Check if the review was approved and by whom
        flag_set = False
        for flag in bug.flags:
            if flag.get('name') == 'fedora-review':
                if flag.get('status') == '+':
                    flag_set = True
                if check_fas and require_auth:
                    fas_user = self.get_fas_user_by_bz_email(bug.creator)
                    if not fas_user:
                        raise ValidationError(
                            'The email address "{0}" of the Bugzilla reviewer '
                            'is not tied to a user in FAS. Group membership '
                            'can\'t be validated.'.format(flag['setter']))
                    if not FAS_CLIENT.user_member_of(fas_user, 'packager'):
                        raise ValidationError('The Bugzilla bug\'s review '
                                              'is approved by a user that is '
                                              'not a packager')
                # Setter will be an empty string and emails will not be shown
                # if the user is not logged in. This is why we check for
                # authentication here.
                if require_auth:
                    if flag['setter'] == bug.creator:
                        error = ('The Bugzilla bug\'s review is approved '
                                 'by the person creating the bug. This is '
                                 'not allowed.')
                        raise ValidationError(error)

                    assigned_to_emails = [bug.assigned_to]
                    if bug.assigned_to in FAS_CLIENT.client.\
                            _AccountSystem__alternate_email:
                        assigned_to_id = FAS_CLIENT.client.\
                            _AccountSystem__alternate_email[bug.assigned_to]
                        assigned_to_user = FAS_CLIENT.get_fas_user_by_id(
                            assigned_to_id)
                        if assigned_to_user:
                            assigned_to_emails.append(
                                assigned_to_user['email'])
                    if flag['setter'] not in assigned_to_emails:
                        raise ValidationError('The review is not approved by '
                                              'the assignee of the Bugzilla '
                                              'bug')

                update_dt = flag.get('modification_date')
                if update_dt:
                    dt = datetime.strptime(
                        update_dt.value, '%Y%m%dT%H:%M:%S')
                    delta = datetime.utcnow().date() - dt.date()
                    if delta.days > 60:
                        raise ValidationError('The Bugzilla bug\'s review '
                                              'was approved over 60 days ago')
                break
        if not flag_set:
            raise ValidationError(
                'The Bugzilla bug is not approved yet')
        # Check the format of the Bugzilla bug title
        tmp_summary = bug.summary.partition(':')[2]
        if not tmp_summary:
            raise ValidationError(
                'Invalid title for this Bugzilla bug (no ":" present)')
        if ' - ' not in tmp_summary:
            raise ValidationError(
                'Invalid title for this Bugzilla bug (no "-" present)')
        pkg_in_bug = tmp_summary.split(' - ', 1)[0].strip()
        if pkg != pkg_in_bug:
            error = ('The package in the Bugzilla bug "{0}" doesn\'t match '
                     'the one provided "{1}"'.format(pkg_in_bug, pkg))
            raise ValidationError(error)
        return bug

    def get_bug_url(self, bug_id):
        """
        Forms the url to a Bugzilla bug
        :param bug_id: a string of the bug ID
        :return: a string of the Bugzilla bug URL
        """
        bz_query_params = urlencode({'id': bug_id})
        return '{0}/show_bug.cgi?{1}'.format(
            self.url.rstrip('/'), bz_query_params)

    def comment(self, bug_id, comment):
        """ Leave a comment on a Bugzilla bug.

        Should not raise an exception, even in the case of failure.

        :param bug_id: a string of the bug ID
        :param comment: a string of the comment to post.
        :return: None
        """

        try:
            click.echo("- Adding comment to rhbz#{0}".format(bug_id))
            bug = self.client.getbug(bug_id)
            bug.addcomment('(fedscm-admin):  ' + comment)
        except Exception:
            import traceback
            click.echo(traceback.format_exc())
            click.echo("! Failed to add comment to %r" % bug_id)
            # Don't fail.  This is not as important.
