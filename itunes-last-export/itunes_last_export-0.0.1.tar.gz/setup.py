#!/usr/bin/python
# -*- coding: utf-8 -*-

import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="itunes_last_export",
    version="0.0.1",
    author="Vincent Verdeil",
    author_email="vincent.verdeil@gmail.com",
    description="ool to import playcounts and loved tracks from your last.fm account into iTunes",
    long_description=long_description,
    url="https://github.com/werdeil/itunes_last_export",
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio',
    ),
)