# -*- coding: utf-8 -*-

import djangoplus
import os
import shutil
from fabric.api import *

password = os.environ.get('TWINE_PASSWORD')
basedir = os.path.dirname(os.path.realpath(os.path.dirname(djangoplus.__file__)))


def release(project=None):

    with lcd(basedir):
        version = None
        new_version = None
        setup_file_path = os.path.join(basedir, 'setup.py')
        setup_file_lines = open(setup_file_path).readlines()
        for i, line in enumerate(setup_file_lines):
            if 'version=' in line:
                version = line.strip()[-4:-2]
                new_version = str(int(version)+1)
                setup_file_lines[i] = setup_file_lines[i].replace(version, new_version)
                break
        if new_version:
            open(setup_file_path, 'w').write(str(''.join(setup_file_lines)))
            github_git_dir_path = os.path.join(basedir, 'djangoplus/.git')
            github_git_tmp_path = '/tmp/djangoplus-version-{}'.format(version)
            print(version, '>>>', new_version)
            print('Moving', github_git_dir_path, github_git_tmp_path)
            shutil.move(github_git_dir_path, github_git_tmp_path)
            local('python setup.py sdist')
            print('Moving', github_git_tmp_path, github_git_dir_path)
            shutil.move(github_git_tmp_path, github_git_dir_path)
            local('twine upload -p{} dist/djangoplus-0.0.{}.tar.gz'.format(password, new_version))


