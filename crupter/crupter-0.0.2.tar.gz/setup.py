# -*- coding: utf-8 -*-


'''setup.py: setuptools control.'''


import re
from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

version = "0.0.2"

setup(
    name='crupter',
    packages=['crupter'],
    entry_points={
        'console_scripts': ['crupter = crupter.cli:main']
    },
    version=version,
    description='Easily CReate, UPdate and TERminate your AWS CloudFormation Stacks.',
    long_description=long_description,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        "boto3 == 1.7.11",
        "botocore == 1.10.11",
        "click == 6.7",
        "click-log == 0.2.1",
        "jmespath == 0.9.3",
        "Jinja2 == 2.10",
        "pyyaml == 3.12",
        "voluptuous == 0.11.1",
        "simplejson == 3.13.2",
        "yamllint == 1.11.0",
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
    url='https://github.com/binxio/crupter',
)
