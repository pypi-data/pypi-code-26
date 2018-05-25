#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyelectrica",
    version="1.0.6",
    author="Isai Aragón",
    author_email="isaix25@gmail.com",
    description="Módulo PyElectrica, útil para resolver problemas específicos en la Ingeniería eléctrica",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/x1sa1/PyElectrica",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Natural Language :: Spanish",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ),
)
