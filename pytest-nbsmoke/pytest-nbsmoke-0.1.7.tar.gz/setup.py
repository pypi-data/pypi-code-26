#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup

import versioneer


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-nbsmoke',
    version=versioneer.get_version(),
    author='pytest-nbsmoke contributors',
    license='BSD-3',
    url='https://github.com/pyviz/nbsmoke',
    description='Deprecated: now nbsmoke (see https://github.com/pyviz/nbsmoke).',
    long_description=read('README.txt'),
    py_modules=['pytest_nbsmoke'],
    install_requires=['pytest>=3.1.1',
                      'jupyter_client',
                      'ipykernel',
                      'nbformat',
                      'nbconvert',
                      'pyflakes'],
    classifiers=[
        'Development Status :: 7 - Inactive',
    ],
    entry_points={
        'pytest11': [
            'nbsmoke = pytest_nbsmoke',
        ],
    },
)
