#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import sys

here = path.abspath(path.dirname(__file__))


setup(
    name='atutils',
    version='0.0.0',
    description="A collection of utilities",
    author='Edgar Y. Walker',
    author_email='eywalker@bcm.edu',
    url='https://github.com/atlab/atutils',
    packages=find_packages(),
    install_requires=[],
)
