#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
from os.path import join, isfile
from os import walk
from pinhole import __version__, __author__


def read_file(filename):
    with open(filename) as fp:
        return fp.read().strip()


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


def package_files(directories):
    paths = []
    for item in directories:
        if isfile(item):
            paths.append(join('..', item))
            continue
        for (path, directories, filenames) in walk(item):
            for filename in filenames:
                paths.append(join('..', path, filename))
    return paths


setup(
    name='Pinhole',
    version=__version__,
    description='Less Is More.',
    long_description=
    'Go to https://github.com/uid00000000/pinhole for more information.',
    author=__author__,
    author_email='markbrownjayb@qq.com',
    url='https://github.com/uid00000000/pinhole',
    license='MIT',
    include_package_data=True,
    packages=find_packages(),
    install_requires=read_requirements('requirements.txt'),

    entry_points={
        'console_scripts': {
            'pinhole = pinhole.run:main'
        },
    },
)
