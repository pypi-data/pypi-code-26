#!/usr/bin/env python3

from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="osafe",
    version="0.1.0",
    description="A Python implementation of OSafe.",
    license="MIT",
    url="https://github.com/osafe/osafe-python",
    author="Oded Niv",
    author_email="oded.niv@gmail.com",
    packages=find_packages(),
    install_requires=[
        'cached-property',
        'pycrypto',
        'google-api-python-client',
        'oauth2client',
    ],
    entry_points={
        'console_scripts': [
            'osafe=osafe.cli:main',
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
