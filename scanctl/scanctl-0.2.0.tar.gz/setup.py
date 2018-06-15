#! /usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import re

from setuptools import find_packages
from setuptools import setup

name = 'scanctl'
here = os.path.abspath(os.path.dirname(__file__))

meta = {}
with open(os.path.join(here, name, '__init__.py')) as f:
    exec(f.read(), meta)


def find_meta(key):
    key = f'__{key}__'
    if key not in meta:
        raise RuntimeError(f'Required metadata key not found: {key}')
    return meta[key]


def requirements(*paths):
    with open(os.path.join(here, *paths)) as f:
        reqs_txt = f.read()
    parsed = [re.split(r'[<~=>]=?', r, maxsplit=2)[0]
              for r in reqs_txt.splitlines() if not r.startswith('-f')]
    return [r for r in parsed if r != '']


def read(*paths, sep='\n', enc='utf-8'):
    buf = []
    for path in paths:
        with codecs.open(os.path.join(here, path), 'rb', enc) as f:
            buf.append(f.read())
    return sep.join(buf)


setup(
    name=find_meta('name'),
    version=find_meta('version'),
    license=find_meta('license'),
    author=find_meta('author'),
    author_email=find_meta('email'),
    maintainer=find_meta('author'),
    maintainer_email=find_meta('email'),
    url=find_meta('url'),
    description=find_meta('description'),
    long_description=read('README.md'),
    keywords=find_meta('keywords'),
    classifiers=find_meta('classifiers'),
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    setup_requires=['pytest-runner'],
    install_requires=requirements('requirements.txt'),
    tests_require=requirements('requirements-test.txt'),
    entry_points={'console_scripts': ['scanctl = scanctl.cli:main']},
    zip_safe=False,
)
