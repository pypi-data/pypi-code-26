#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

install_requires = [
    'dpkt>=1.9.0'
]
setup_requires = [
    'pytest-runner>=2.9',
]
tests_require = [
    'pytest>=3.0.0',
    'pytest-cov>=2.4.0',
]

setup(
    name='tcp_reader',
    version='0.1.0.post1',
    description='TCP Stream Reader',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Simon Wörner',
    author_email='git@simon-woerner.de',
    url='https://git.brn.li/SWW13/tcp-reader-py',
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
