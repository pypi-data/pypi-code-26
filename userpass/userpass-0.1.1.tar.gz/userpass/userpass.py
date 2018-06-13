#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User
Load and store userinfo.

Default save user info(username and password) at $HOME
"""

import os
import os.path
import pickle
import getpass


class User(object):
    """Contain username and password."""

    def __init__(self, path='.userpass', hint='input user info'):
        """init User
        :param path: where to store username and password.
        """
        self._hint = hint
        self._path = path
        home = os.path.expanduser('~')
        self._filename = os.path.join(home, self._path)
        if not os.path.exists(self._filename):
            self._data = {}
            self.set_user()
        else:
            self._data = self._load()

    def _load(self):
        """load user info from self._filename
        :return: userinfo dict{username,password}
        """
        with open(self._filename, 'rb') as file:
            return pickle.load(file)

    def _store(self):
        """store user info to self._filename
        :return: None
        """
        with open(self._filename, 'wb') as file:
            pickle.dump(self._data, file)
        os.chmod(self._filename, 0o600)

    def set_user(self):
        """init set user info
        :return: None
        """
        print(self._hint)
        username = input('Username: ').encode()
        password = getpass.getpass().encode()
        self._data['username'] = username
        self._data['password'] = password
        self._store()

    def del_user(self):
        """delete userinfo file
        :return: None
        """
        if os.path.exists(self._filename):
            os.remove(self._filename)

    @property
    def username(self):
        """username
        :return: username bytes
        """
        return self._data['username']

    @property
    def password(self):
        """password
        :return: password bytes
        """
        return self._data['password']

    def show(self):
        """show username
        :return: None
        """
        print(type(self.username))
        print(self.username)
