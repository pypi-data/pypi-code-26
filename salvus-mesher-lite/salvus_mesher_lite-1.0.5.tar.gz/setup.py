#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This file is part of the lite version of the SalvusMesher package intended to
produce meshes for AxiSEM3D. If you are looking for the full version head
over to http://mondaic.com.

:copyright:
    Copyright (C) 2016-2018 Salvus Development Team <www.mondaic.com>,
                            ETH Zurich
:license:
    GNU General Public License, Version 3 [academic use only]
    (http://www.gnu.org/copyleft/gpl.html)
"""
from setuptools import find_packages, setup
from setuptools.extension import Extension

import inspect
import os
import sys


# Import the version string.
path = os.path.join(os.path.abspath(os.path.dirname(inspect.getfile(
    inspect.currentframe()))), "salvus_mesher_lite")
sys.path.insert(0, path)
from version import get_git_version  # NOQA


DOCSTRING = __doc__.strip().split("\n")


def get_package_data():
    """
    Returns a list of all files needed for the installation relativ to the
    "salvus_mesher_lite" subfolder.
    """
    filenames = []
    # The lasif root dir.
    root_dir = os.path.join(os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe()))), "salvus_mesher_lite")
    # Recursively include all files in these folders:
    folders = [
        # Data
        os.path.join(root_dir, "data"),
        # input schema
        os.path.join(root_dir, "interface", "schemas"),
        # test data.
        os.path.join(root_dir, "tests", "data"),
    ]
    for folder in folders:
        for directory, _, files in os.walk(folder):
            for filename in files:
                # Exclude hidden files.
                if filename.startswith("."):
                    continue
                filenames.append(os.path.relpath(
                    os.path.join(directory, filename),
                    root_dir))
    filenames.append("RELEASE-VERSION")
    return filenames


src = os.path.join('salvus_mesher_lite', 'src')
lib = Extension('salvus_mesher_lite',
                sources=[
                    os.path.join(src, "angle.c"),
                    os.path.join(src, "connectivity.c"),
                    os.path.join(src, "centroid.c"),
                    os.path.join(src, "hmin_max.c"),
                    os.path.join(src, "facets.c"),
                    os.path.join(src, "sort.c")])


INSTALL_REQUIRES = ["numpy",
                    "scipy",
                    "matplotlib",
                    "jsonschema",
                    "pyyaml",
                    "pytest",
                    "flake8",
                    "pytest-mpl"]


# Add mock for Python 2.x. Starting with Python 3 it is part of the standard
# library.
if sys.version_info[0] == 2:
    INSTALL_REQUIRES.append("mock")

setup_config = dict(
    name="salvus_mesher_lite",
    version=get_git_version(),
    description=DOCSTRING[0],
    long_description="\n".join(DOCSTRING[2:]),
    author=u"Martin van Driel",
    author_email="Martin@vanDriel.de",
    url="https://salvus.io",
    packages=find_packages(),
    package_data={
        "salvus_mesher_lite":
            [os.path.join("lib", "salvus_mesher_lite.so")] +
            get_package_data()},
    license="",
    platforms="OS Independent",
    install_requires=INSTALL_REQUIRES,
    ext_package='salvus_mesher_lite.lib',
    ext_modules=[lib],
    # this is needed for "pip install instaseis==dev"
    classifiers=[
        # complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics"
        ],
)


if __name__ == "__main__":
    setup(**setup_config)