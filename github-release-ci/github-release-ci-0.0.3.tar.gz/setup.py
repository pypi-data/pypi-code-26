#!/usr/bin/env python
# coding=utf-8
"""Setup script."""

import sys
from os import path
from setuptools import setup, find_packages

dependencies = ['requests', 'click']
name = "github-release-ci"
desc = "Deployment script for github aimed at using CI"
license = "MIT"
url = "https://github.com/hiroaki-yamamoto/github_release_ci"
keywords = "deployment github"
version = "0.0.0"

version_file = \
    path.join(path.abspath(path.dirname(__file__)), "VERSION")

if path.exists(version_file):
    with open(version_file) as v:
        version = v.read()

author = "Hiroaki Yamamoto"
author_email = "hiroaki@hysoftware.net"

if sys.version_info < (2, 7):
    raise RuntimeError("Not supported on earlier then python 2.7.")

try:
    with open('README.md') as readme:
        long_desc = readme.read()
except Exception:
    long_desc = None

setup(
    name=name,
    version=version,
    description=desc,
    long_description=long_desc,
    packages=find_packages(exclude=["tests"]),
    install_requires=dependencies,
    zip_safe=False,
    author=author,
    author_email=author_email,
    license=license,
    keywords=keywords,
    url=url,
    entry_points={
        'console_scripts': [
            "download=github_release_ci.download:main",
            "upload=github_release_ci.upload:main"
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5"
    ]
)
