#!/usr/bin/env python
# -*- coding: utf-8 -*-

import imp
import os
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
curr_path = os.path.dirname(os.path.realpath(__file__))
deps = os.path.join(curr_path, 'requirements.txt')
dev_deps = os.path.join(curr_path, 'dev_requirements.txt')

requirements = open(deps).read()
test_requirements = open(dev_deps).read()

CODE_DIRECTORY = 'bubble3'
metadata = imp.load_source(
    'metadata', os.path.join(CODE_DIRECTORY, 'metadata.py'))

#orderdict needed for structlog
sys_version_str='.'.join((str(s) for s in sys.version_info[0:3]))


setup(
    name=metadata.package,
    version=metadata.version,
    author=metadata.authors[0],
    author_email=metadata.emails[0],
    maintainer=metadata.authors[0],
    maintainer_email=metadata.emails[0],
    url=metadata.url,
    description=metadata.description,
    long_description=readme + '\n\n' + history,
    packages=[
        'bubble3',
        'bubble3.util',
        'bubble3.util.dataset',
        'bubble3.util.store',
        'bubble3.commands',
        'bubble3.clients',
    ],
    package_dir={'bubble3':
                 'bubble3'},
    py_modules=['bubble3'],
    include_package_data=True,
    install_requires=requirements,
    license="GPL-3.0",
    zip_safe=False,
    keywords='bubble, api2api, transform',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Environment :: Console',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points='''
        [console_scripts]
        bubble = bubble3.cli:cli
        bubble3 = bubble3.cli:cli
    '''
)
