# -*- coding: utf-8 -*-
"""
Created on Sun Jun 10 21:28:51 2018

@author: Jiacuo
"""

#!/usr/bin/env python
# coding=utf-8

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coincap",
    version="1.0",
    author="jaicuo",
    author_email="448117031@qq.com",
    description="A small package for history data of crypto currency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BurgessFANG/coincap",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)