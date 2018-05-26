#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from muriki import __version__
from codecs import open
from os import path
current_dir = path.abspath(path.dirname(__file__))

with open(path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(current_dir, 'LICENSE'), encoding='utf-8') as f:
    license_ = f.read()



# the setup
setup(
    name = 'muriki',
    packages = ['muriki'], # this must be the same as the name above
    version=__version__,
    description='An utility to import data and persist data',
    license=license_,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Humberto Ramos Costa',
    author_email='1bertorc@gmail.com',
    url = 'https://github.com/1ber/muriki',
    download_url = 'https://github.com/1ber/muriki/archive/0.1.tar.gz',
    keywords = ['muriki', 'import', 'csv', 'fixed length', 'database'],
    classifiers = [],
    data_files = [("", ["LICENSE"])]
)
