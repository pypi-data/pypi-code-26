#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from pydgutils_bootstrap import use_pydgutils
use_pydgutils()

import os
import os.path
import sys
import shutil
import logging
import fnmatch
import pydgutils
from setuptools import setup, find_packages

package_name = "rabird.html"

our_packages, source_dir = pydgutils.process_packages()

with open('README.rst') as readme_file, open('HISTORY.rst') as history_file:
    long_description = (readme_file.read() + "\n\n" + history_file.read())

install_requires = [
    # TODO: put package requirements here
    'rabird.core',
]

setup_requires = [
    'pytest-runner',
    # TODO(starofrainnight): put setup requirements (distutils extensions, etc.) here
]

tests_requires = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='rabird.html',
    version='0.0.2',
    description="Provided some utilities that help html parsing",
    long_description=long_description,
    author="Hong-She Liang",
    author_email='starofrainnight@gmail.com',
    url='https://github.com/starofrainnight/rabird.html',
    packages=our_packages,
    package_dir={"": source_dir},
    include_package_data=True,
    install_requires=install_requires,
    license="Apache Software License",
    zip_safe=False,
    keywords='rabird.html',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=tests_requires,
    setup_requires=setup_requires,
)
