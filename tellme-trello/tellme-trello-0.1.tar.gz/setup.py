#!/usr/bin/env python
from setuptools import setup, find_packages
import tellme_trello


def read_file(name):
    with open(name) as fd:
        return fd.read()

keywords = ['django', 'web', 'html']

setup(
    name='tellme-trello',
    version=tellme_trello.__version__,
    description=tellme_trello.__doc__,
    long_description=read_file('README.rst'),
    author=tellme_trello.__author__,
    author_email=tellme_trello.__email__,
    license=tellme_trello.__license__,
    url=tellme_trello.__url__,
    keywords=keywords,
    packages=find_packages(exclude=[]),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
