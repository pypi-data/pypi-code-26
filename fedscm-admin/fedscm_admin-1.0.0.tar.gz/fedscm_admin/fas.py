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
Provides helper functions for FAS
"""
from __future__ import absolute_import

from fedora.client import AccountSystem, AuthError
from click import ClickException


class FASClient(object):
    """
    A helper class to maintain a FAS session
    """
    def __init__(self):
        self.client = AccountSystem('https://admin.fedoraproject.org/accounts')
        self.unauthenticated_error = (
            'The FAS Client is not authenticated. Please make sure you typed '
            'in the correct credentials.')

    def set_credentials(self, username, password):
        """
        A login function to FAS. If the password is incorrect, a ClickException
        is raised.
        :param username: a string of the username
        :param password: a string of the password
        :return: None
        """
        if not self.client.verify_password(username, password):
            raise ClickException(
                'The login to FAS failed. Please make sure you typed in the '
                'correct credentials.')
        self.client.username = username
        self.client.password = password

    def get_fas_user_by_id(self, user_id):
        """
        Get the FAS user based on the user ID
        :param user_id: an integer of the FAS user ID
        """
        try:
            return self.client.person_by_id(user_id)
        except AuthError:  # pragma: no cover
            raise ClickException(self.unauthenticated_error)

    def get_fas_user(self, value, search_key='username'):
        """
        Taken from:
        https://pagure.io/pkgdb-cli/blob/master/f/pkgdb2client/utils.py

        Get the FAS user associated with the provided key value
        If an email address is used, it can be either the FAS email address or
        the one used in Bugzilla.
        :param value: a string to search for
        :param search_key: a string of the key to search for. This defaults to
        email
        :return: a FAS user or None
        """
        email = None
        if search_key == 'email':
            email = value
        if email and email in self.client._AccountSystem__alternate_email:
            user_id = self.client._AccountSystem__alternate_email[email]
        else:
            try:
                user_id = self.client.people_query(
                    constraints={search_key: value},
                    columns=['id']
                )
            except AuthError:  # pragma: no cover
                raise ClickException(self.unauthenticated_error)
            if user_id:
                user_id = user_id[0].id

        if user_id:
            return self.get_fas_user_by_id(user_id)
        return None

    @staticmethod
    def user_member_of(user, group):
        """
        Checks
        :param user: a FAS user object
        :param group: a string of the FAS group
        :return: boolean
        """
        return user and group in user['group_roles'] \
            and user['group_roles'][group]['role_status'] == 'approved'
