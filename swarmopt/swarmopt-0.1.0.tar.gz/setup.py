#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools 

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="swarmopt",
    version="0.1.0",
    description="Swarm intelligence hyperparameter optimization.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/siokcronin/swarmopt",
    author="Siobhán K Cronin",
    author_email="siobhankcronin@gmail.com",
    license="MIT",
    keywords="swarmopt",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    zip_safe=False,
)
