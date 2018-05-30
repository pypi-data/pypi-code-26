# -*- coding: utf-8 -*-

import os
import datetime
from fabric.api import *
from os import path
import time
EMPTY_TEST_FILE_CONTENT = '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangoplus._test_admin.models import User
from djangoplus.test import TestCase
from django.conf import settings


class AppTestCase(TestCase):

    def test_app(self):

        User.objects.create_superuser('_test_admin', None, settings.DEFAULT_PASSWORD)

        self.login('_test_admin', settings.DEFAULT_PASSWORD)
'''


DOCKER_FILE_CONTENT = '''FROM {}

RUN apt-get update
RUN apt-get -y install python3 python3-pip build-essential python3-dev libfreetype6-dev python3-cffi libtiff5-dev liblcms2-dev libwebp-dev tk8.6-dev libjpeg-dev ssh openssh-server dnsutils curl vim git
RUN apt-get -y install chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev wget

RUN apt-get -y install libgtk-3-dev
RUN wget https://ftp.mozilla.org/pub/firefox/releases/60.0b3/linux-x86_64/en-US/firefox-60.0b3.tar.bz2
RUN tar xvjf firefox-60.0b3.tar.bz2
RUN ln -s /firefox/firefox /usr/local/bin/firefox
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.20.0/geckodriver-v0.20.0-linux64.tar.gz
RUN gunzip geckodriver-v0.20.0-linux64.tar.gz
RUN tar -xvf geckodriver-v0.20.0-linux64.tar
RUN mv geckodriver /usr/local/bin/

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN export LANG=C.UTF-8

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -sfn /usr/bin/python3 /usr/bin/python

RUN pip install --upgrade pip
'''

PROJECTS = [
    ('companies', 'git@djangoplus.net:companies.git'),
    ('blackpoint', 'git@bitbucket.org:brenokcc/blackpoint.git'),
    ('emprestimos', 'git@djangoplus.net:emprestimos.git'),
    ('financeiro', 'git@bitbucket.org:brenokcc/financeiro.git'),
    ('formulacao', 'git@bitbucket.org:brenokcc/formulacao.git'),
    ('gouveia', 'git@bitbucket.org:brenokcc/gouveia.git'),
    ('petshop', 'git@bitbucket.org/brenokcc/petshop.git'),
    ('loja', 'git@bitbucket.org/brenokcc/loja.git'),
    ('biblioteca', 'git@bitbucket.org/brenokcc/biblioteca.git'),
    ('gerifes', 'git@bitbucket.org/brenokcc/gerifes.git'),
    ('simop', 'git@bitbucket.org/brenokcc/simop.git'),
    ('fabrica', 'git@bitbucket.org:brenokcc/fabrica.git'),
    ('abstract', 'git@bitbucket.org:brenokcc/abstract.git'),
]


def _test_startpoject():
    if path.exists('/tmp/xxx'):
        local('rm -r /tmp/xxx')
    with lcd('/tmp/'):
        local('startproject xxx')
        with lcd('/tmp/xxx'):
            local('python manage.py test')
        with lcd('/tmp'):
            local('rm -r /tmp/xxx')


def _test_admin():
    local('python manage.py test djangoplus.admin.tests.AdminTestCase')


def _test_projects():
    from subprocess import Popen, PIPE
    paths = []
    start = datetime.datetime.now()
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    for project_name, project_url in PROJECTS:
        if path.exists('/Users/breno'):
            base_path = '/Users/breno/Documents/Workspace'
            if project_name in ('petshop', 'loja', 'biblioteca'):
                base_path = path.join(base_path, 'djangoplus/djangoplus-demos')
            project_path = path.join(base_path, project_name)
        else:
            project_path = path.join('/tmp', project_name)
            if not path.exists(project_path):
                local('git clone {} {}'.format(project_url, project_path))
            with lcd(project_path):
                local('git pull origin master')
        paths.append(project_path)

    running_procs = []
    for project_path in paths:
        project_name = project_path.split('/')[-1]
        print('Testing {}'.format(project_name))
        with lcd(project_path):
            local('python manage.py test')
        # proc = Popen(['python', 'manage.py', 'test'], cwd=project_path, stderr=PIPE, stdout=PIPE)
        # proc.project_name = project_name
        # running_procs.append(proc)

    while running_procs:
        for proc in running_procs:
            retcode = proc.poll()
            if retcode is not None:
                running_procs.remove(proc)
                if retcode != 0 and retcode != -9:
                    print('An error was found while executing "{}"!'.format(proc.project_name))
                    print(proc.stderr.read())
                    for uncessary_proc in running_procs:
                        print('Killing execution for "{}"...'.format(uncessary_proc.project_name))
                        uncessary_proc.kill()
            else:
                time.sleep(5)
                continue
    end = datetime.datetime.now()
    print('Tests executed in "{}" seconds!!!'.format((end-start).seconds))


def _test_testcases_generation():
    test_file_path = '{}/emprestimos/emprestimos/tests.py'.format('/Users/breno/Documents/Workspace')
    test_file_content = open(test_file_path).read()
    open(test_file_path, 'w').write(EMPTY_TEST_FILE_CONTENT)
    with lcd('{}/emprestimos'.format('/Users/breno/Documents/Workspace')):
        local('python manage.py test --add')
    print(open(test_file_path).read())
    open(test_file_path, 'w').write(test_file_content)


def _test_so_installation(so):
    docker_file = open('/tmp/Dockerfile', 'w')
    docker_file.write(DOCKER_FILE_CONTENT.format(so))
    docker_file.close()
    local('docker build -t djangoplus-{} /tmp'.format(so))
    local('docker run djangoplus-{} pip install djangoplus && startproject xyz && cd xyz && python manage.py test djangoplus.admin.tests.AdminTestCase'.format(so))


def _test_deploy():
    pass


def test(scope=''):
    if scope in ('startproject', 'all'):
        _test_startpoject()
    if scope in ('admin', 'all'):
        _test_admin()
    elif scope in ('implementation', 'all'):
        _test_projects()
    elif scope in ('installation', 'all'):
        _test_so_installation('debian')
        _test_so_installation('ubuntu')
    elif scope in ('deploy', 'all'):
        _test_deploy()
    else:
        print('Available parameters: startproject, admin, implementation, installation, deploy')

