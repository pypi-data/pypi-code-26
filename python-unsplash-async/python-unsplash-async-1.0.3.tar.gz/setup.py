#!/usr/bin/env python
# coding=utf-8

import uuid
from setuptools import setup, find_packages

with open('unsplash/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'


REQUIRES = [
    'oauthlib>=2.0.1',
    'requests>=2.13.0',
    'requests-oauthlib>=0.7.0',
    'six>=1.10.0',
    'aiohttp',
]

setup(
    name="python-unsplash-async",
    version=version,
    description="A Python client for the Unsplash API.",
    license="MIT",
    maintainer="Alin Panaitiu",
    maintainer_email="alin.p32@gmail.com",
    author="Yakup Adaklı",
    author_email="yakup.adakli@gmail.com",
    url="http://github.com/alin23/python-unsplash",
    packages=find_packages(exclude=["tests"]),
    install_requires=REQUIRES,
    keywords="unsplash library",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    zip_safe=True,
)
