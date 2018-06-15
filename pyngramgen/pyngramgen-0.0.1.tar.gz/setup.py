#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name='pyngramgen',
    version="0.0.1",
    author="huyifeng",
    author_email="solopointer@qq.com",
    description="Generate ngram iterator",
    long_description=open("README.md").read(),
    license="MIT",
    keywords = ("ngram"),
    url="https://github.com/solopointer/pyngramgen",
    packages=['pyngramgen'],
    include_package_data = True,
    install_requires=[],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
)

