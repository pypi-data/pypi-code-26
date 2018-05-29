# -*- coding: utf-8 -*-


'''setup.py: setuptools control.'''


import re
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

version = "0.0.1"

setup(
    name='binx-cli-template',
    packages=['binx'],
    entry_points={
        'console_scripts': ['binx-cli-template = binx.cli:main']
    },
    version=version,
    description='This is just a template to create a new cli',
    long_description=long_description,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        "click == 6.7",
        "click-log == 0.2.1",
        "pyyaml == 3.12",
        "simplejson == 3.13.2",
        "configparser == 3.5.0"
    ],
    extras_require={
        'test': [
            "mock",
            "pytest",
            "pytest-mock",
            "pytest-cov",
            "tzlocal"
        ]
    },
    author='Martijn van Dongen',
    author_email='martijnvandongen@binx.io',
    url='https://github.com/binxio/pipy-cli-template',
)
