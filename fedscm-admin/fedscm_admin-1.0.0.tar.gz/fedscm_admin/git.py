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
Git helper functions
"""
from __future__ import absolute_import
import subprocess as sp
import tempfile
import shutil
import os

import yaml
import click


class GitException(Exception):
    """
    An exception used by the GitRepo class
    """
    pass


class GitRepo(object):
    """
    A class that wraps git commands. It was inspired by the SCM class in the
    Module Build Service.
    """
    def __init__(self, git_url):
        """
        The constructor of the GitRepo class. It creates a temporary directory
        to clone the repo in.
        :param git_url: the URL to clone the git repo from
        """
        self.git_url = git_url
        self.clone_dir = tempfile.mkdtemp()
        # This only exists after the clone happens
        self.git_dir = os.path.join(self.clone_dir, '.git')

    def __del__(self):
        """
        The destructor which deletes the temporary directory on object
        destruction
        :return: None
        """
        if os.path.exists(self.clone_dir):
            shutil.rmtree(self.clone_dir)

    def _assert_cloned(self):
        """
        A helper function to make sure a Git repo is cloned or else a
        GitException is thrown
        :return: None or GitException
        """
        if not os.path.exists(self.git_dir):
            raise GitException('The git repository is not cloned yet')

    def _run_git_cmd(self, command, return_stdout=False):
        """
        A helper function that wraps running a git command
        :param command: a list representing the git command to run. For
        example ['git', 'push']
        :param return_stdout: a bool determining whether or not to return
        stdout
        :return: None, GitException, or a string with stdout
        """
        git_proc = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE,
                            cwd=self.clone_dir)
        stdout, stderr = git_proc.communicate()
        if git_proc.returncode != 0:
            if type(stderr) == bytes:
                stderr = stderr.decode('utf-8').strip()
            else:
                stderr = stderr.strip()
            error_msg = ('The git command "{0}" failed with "{1}"'
                         .format(' '.join(command), stderr))
            raise GitException(error_msg)
        if return_stdout:
            if type(stdout) == bytes:
                return stdout.decode('utf-8').strip()
            else:
                return stdout.strip()

    @property
    def current_branch(self):
        """
        Determines the current branch that is checked out
        :return: a string of the current branch or GitException
        """
        self._assert_cloned()
        command = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        return self._run_git_cmd(command, return_stdout=True)

    @property
    def initialized(self):
        """
        Determines if the git repo has been initialized yet
        """
        self._assert_cloned()
        command = ['git', 'log', '--pretty=oneline']
        try:
            self._run_git_cmd(command, return_stdout=True)
            return True
        except GitException as error:
            if 'does not have any commits yet' in str(error):
                return False
            else:
                raise

    @property
    def initialized_remotely(self):
        """
        Determines if the git repo is initialized by using `git ls-remote`.
        """
        command = ['git', 'ls-remote', self.git_url]
        output = self._run_git_cmd(command, return_stdout=True)
        return 'refs/remotes/origin/master' in output or \
            'refs/heads/master' in output

    @property
    def first_commit(self):
        """
        Get the first commit on the master branch
        :return: a string of the first commit or None
        """
        self._assert_cloned()
        # If the git repo is not initialized then there is no commit to get
        if not self.initialized:
            return None

        command = ['git', 'rev-list', '--max-parents=0', 'master']
        commits = self._run_git_cmd(command, return_stdout=True)
        if commits:
            # Return the last one on the screen which is the first commit
            return commits.split()[-1]
        else:
            return None

    def clone_repo(self):
        """
        Clones the repo based on the URL passed in the construction of the
        GitRepo object
        :return: None or GitException
        """
        # Don't clone it again if it's already been cloned
        if not os.path.exists(self.git_dir):
            click.echo('- Cloning {0}'.format(self.git_url))
            clone_cmd = ['git', 'clone', '-q', self.git_url, self.clone_dir]
            self._run_git_cmd(clone_cmd)

    def checkout_branch(self, branch_name, new=False):
        """
        Checks out a branch
        :param branch_name: a string of the branch to checkout
        :param new: a boolean determining if the branch is new
        :return: None or GitException
        """
        self._assert_cloned()
        checkout_cmd = ['git', 'checkout']
        if new is True:
            checkout_cmd.append('-b')
        checkout_cmd.append(branch_name)
        self._run_git_cmd(checkout_cmd)

    def new_branch(self, branch_name):
        """
        Creates a new branch and pushes it to the remote Git server
        :param branch_name: a string of the branch to checkout
        :return: None or GitException
        """
        self._assert_cloned()
        push_cmd = ['git', 'push', '--set-upstream',
                    'origin', branch_name]
        # Checkout the new branch
        self.checkout_branch(branch_name, new=True)
        # Push the new branch to the git server
        self._run_git_cmd(push_cmd)
        # Checkout master once we're done pushing the new branch
        self.checkout_branch('master')

    def add(self, file_name):
        """
        Stages a file for commit
        :param file_name: a string of the file name to stage
        :return: None or GitException
        """
        self._assert_cloned()
        add_cmd = ['git', 'add', file_name]
        self._run_git_cmd(add_cmd)

    def commit(self, commit_msg):
        """
        Commits the staged changes
        :param commit_msg: a string of the commit message
        :return: None or GitException
        """
        self._assert_cloned()
        click.echo('- Committing to {0}'.format(self.git_url))
        push_cmd = ['git', 'commit', '-m', '"' + commit_msg + '"']
        self._run_git_cmd(push_cmd)

    def push(self):
        """
        Pushes the committed changes to the Git server
        :return: None or GitException
        """
        self._assert_cloned()
        click.echo('- Pushing to {0}'.format(self.git_url))
        push_cmd = ['git', 'push']
        self._run_git_cmd(push_cmd)

    def set_monitoring_on_repo(self, namespace, repo, monitoring_level):
        """
        Set the monitoring level of a repo in config.yml
        :param namespace: the dist-git namespace of the package in question.
        :param repo: the name of the dist-git repo in question.
        :param monitoring_level: a string representing the desired monitoring
        level
        :return: None or GitException
        """
        self._assert_cloned()

        if self.current_branch != 'master':
            self.checkout_branch('master')

        config_yml_dir = os.path.join(self.clone_dir, namespace)
        if not os.path.exists(config_yml_dir):
            os.makedirs(config_yml_dir)

        config_yml_path = os.path.join(config_yml_dir, repo)
        config_yml_file = {}
        if os.path.exists(config_yml_path):
            with open(config_yml_path, 'r') as config_yml_stream:
                config_yml_file = yaml.load(config_yml_stream)

        # Cast it as a string to make sure it outputs correctly in the yml
        # output. If it's unicode, then it will output with "!!python-unicode"
        # in front of it.
        config_yml_file['monitoring'] = str(monitoring_level)

        with open(config_yml_path, 'w') as config_yml_stream:
            yaml.dump(config_yml_file, config_yml_stream,
                      default_flow_style=False)

        self.add(config_yml_path)
        self.commit('Adding monitoring for {0}/{1}'.format(namespace, repo))
        self.push()
