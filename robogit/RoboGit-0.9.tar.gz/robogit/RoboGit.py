import os
from git import Repo
from robot.api import logger
from shutil import rmtree


class RoboGit(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        pass

    def clone_repository_from_url(self, repo_url, to_path, branch = None):
        '''
        Clones a repo from a URL to a particular path on your local system. Branch is optional
        :param repo_url: url for the repo
        :param to_path: local directory to clone to
        :param branch:
        :return:
        '''

        if branch:
            Repo.clone_from(url = repo_url, to_path = to_path, branch=branch)
        else:
            Repo.clone_from(url=repo_url, to_path=to_path)

    def clear_contents_from_directory(self, path):
        rmtree(path)
        if not os.path.exists(path):
            os.makedirs(path)
